import re
from pathlib import Path

import pypdf
from dotenv import load_dotenv

load_dotenv()

HEADING = re.compile(r"^(\d+)\. (.+)")


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
    return chunks
