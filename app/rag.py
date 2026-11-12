import os
import re
from functools import cache
from pathlib import Path

import numpy as np
import pypdf
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

HEADING = re.compile(r"^(\d+)\. (.+)")
MIN_SCORE = 0.65  # cosine of the top hit; answerable questions score >= 0.717, off-topic ones <= 0.58
NOT_FOUND = "I could not find this in the plant documents I have. Please check with your supervisor or the QMS."
SYSTEM = (
    "You help shop-floor supervisors at a manufacturing plant. Answer ONLY from the numbered excerpts. "
    "If the excerpts do not contain the answer, reply with exactly NOT_FOUND and nothing else. "
    "Be short and practical: give exact values with units, short numbered steps for procedures, and include "
    "any conditions, exceptions or safety warnings the excerpt states. Name the document number you used. "
    "Do not write excerpt numbers like [1] in the answer text. Refer to documents only by document number and revision. "
    "On the last line write SOURCES: followed by the excerpt numbers you used, comma separated."
)
INDEX = None  # (chunks, matrix), built once by build_index()


@cache
def client():
    return genai.Client()  # reads GEMINI_API_KEY


def load_chunks(docs_dir="docs"):
    """One chunk per numbered section of every PDF in docs_dir."""
    chunks = []
    for path in sorted(Path(docs_dir).glob("*.pdf")):
        pages = [p.extract_text() or "" for p in pypdf.PdfReader(path).pages]
        doc_no, rev = re.search(r"Document No\.\s+(\S+)\s+Revision\s+(\d+)", pages[0]).groups()
        effective = re.search(r"Effective Date\s+(\S+)", pages[0]).group(1)
        footer = re.compile(rf"^{re.escape(doc_no)}\s*\|\s*Rev|^Page \d+$")
        lines = [
            (n, line.strip())
            for n, text in enumerate(pages, 1)
            for line in text.splitlines()
            if line.strip() and not footer.match(line.strip())
        ]
        title = lines[1][1]  # line 0 is the company name

        sections, last, i = [], 0, 0
        while i < len(lines):
            page, line = lines[i]
            i += 1
            m = HEADING.match(line)
            # Numbered procedure steps look like headings, so a heading must be the next number,
            # short, and not a sentence.
            if m and int(m[1]) == last + 1 and not line.endswith(".") and len(line) <= 70:
                heading = m[2].strip()
                if line.count("(") > line.count(")") and i < len(lines):  # wrapped heading
                    heading += " " + lines[i][1]
                    i += 1
                last += 1
                sections.append({"section": last, "heading": heading, "page": page, "body": []})
            elif sections:  # text before section 1 is the header block, dropped
                sections[-1]["body"].append(line)

        for s in sections:
            body = "\n".join(s.pop("body"))
            tag = f"[{doc_no} Rev {rev} | {title} | Section {s['section']}. {s['heading']}]"
            chunks.append({
                "id": f"{doc_no}-R{rev}-S{s['section']}",
                "doc_no": doc_no,
                "rev": rev,
                "effective": effective,
                "title": title,
                **s,
                "file": path.name,
                "text": f"{tag}\n{body}",
            })

    # Mark revisions: only the highest revision of each document is current.
    latest = {}
    for c in chunks:
        if int(c["rev"]) > int(latest.get(c["doc_no"], {"rev": -1})["rev"]):
            latest[c["doc_no"]] = c
    for c in chunks:
        new = latest[c["doc_no"]]
        c["current"] = c["rev"] == new["rev"]
        if not c["current"]:
            c["superseded_by"] = new["rev"]
            c["superseded_by_effective"] = new["effective"]
    return chunks


def embed(texts, task_type):
    res = client().models.embed_content(
        model=os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001"),
        contents=texts,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    m = np.array([e.values for e in res.embeddings], dtype=np.float32)
    return m / np.linalg.norm(m, axis=1, keepdims=True)


def build_index():
    global INDEX
    chunks = load_chunks()
    INDEX = (chunks, embed([c["text"] for c in chunks], "RETRIEVAL_DOCUMENT"))
    return INDEX


def retrieve(question, k=4):
    chunks, matrix = INDEX or build_index()
    scores = matrix @ embed([question], "RETRIEVAL_QUERY")[0]
    return [(chunks[i], float(scores[i])) for i in np.argsort(-scores)[:k]]


def answer(question):
    ranked = retrieve(question, k=8)
    hits = [h for h in ranked if h[0]["current"]][:4]  # only current revisions reach the model
    if not hits or hits[0][1] < MIN_SCORE:
        return {"answer": NOT_FOUND, "found": False, "sources": [], "notice": None}
    notices = {}  # one notice per superseded doc_no + rev
    for c, _ in ranked[:4]:
        if not c["current"]:
            notices[(c["doc_no"], c["rev"])] = (
                f"{c['doc_no']} Rev {c['rev']} (effective {c['effective']}) also matched your question but is "
                f"superseded by Rev {c['superseded_by']} (effective {c['superseded_by_effective']}). "
                f"This answer uses Rev {c['superseded_by']} only. Do not use printed Rev {c['rev']} copies."
            )

    excerpts = "\n\n".join(f"[{n}] {c['text']}" for n, (c, _) in enumerate(hits, 1))
    response = client().models.generate_content(
        model=os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite"),
        contents=f"Excerpts:\n\n{excerpts}\n\nQuestion: {question}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            temperature=0,
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )
    reply = (response.text or "").strip()  # text is None when the reply is blocked or empty
    if not reply or reply.startswith("NOT_FOUND"):
        return {"answer": NOT_FOUND, "found": False, "sources": [], "notice": None}

    lines = reply.splitlines()
    used = []
    if lines and (m := re.match(r"(?i)\s*SOURCES:\s*(.*)", lines[-1])):
        lines.pop()
        used = [int(n) for n in re.findall(r"\d+", m[1]) if 1 <= int(n) <= len(hits)]
    used = sorted(set(used)) or [1]  # fall back to the top excerpt
    keys = ("doc_no", "rev", "effective", "title", "section", "heading", "page", "file")
    sources = [{**{key: hits[n - 1][0][key] for key in keys}, "score": hits[n - 1][1], "current": True} for n in used]
    text = re.sub(r"\s*\[\d+(?:\s*,\s*\d+)*\]", "", "\n".join(lines))  # excerpt refs like [1], [2, 3]
    text = re.sub(r"\[(Document:[^\]]*)\]", r"\1", text)  # "[Document: X]" -> "Document: X"
    text = re.sub(r"\n\s*Document:\s*$", "", text.strip())  # dangling "Document:" last line
    text = text.replace("**", "")  # the UI shows plain text, so drop markdown bold markers
    return {"answer": text.strip(), "found": True, "sources": sources, "notice": " ".join(notices.values()) or None}
