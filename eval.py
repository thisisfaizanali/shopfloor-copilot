"""Run: .venv\\Scripts\\python eval.py  (exit code 1 if a required check fails)."""
import sys

from app import rag

sys.stdout.reconfigure(encoding="utf-8")

# (id, question, expected found, substrings the answer must contain ("!x" = must not contain x), required,
#  optional substring the revision notice must contain)
QUESTIONS = [
    ("S1", "What is the recommended coolant concentration for the TX-200 CNC turning centre?", True, ["6", "8"], True),
    ("S2", "The machine is showing alarm AL-104. What does it mean and what should the operator do?", True, ["lube"], True),
    ("S3", "Who is allowed to remove a lockout lock from a machine?", True, ["own"], True),
    ("S4", "What is the outer diameter tolerance for the BH-220 bearing housing?", True, ["0.05"], True),
    ("S5", "How often should spindle runout be checked, and who does it?", True, ["month"], True),
    ("O1", "A lot of 600 pieces arrived. How many samples do we inspect and how many minor defects are allowed?", True, ["32"], True, "Rev 03"),
    ("O2", "The supplier did not send the material test certificate. Can we still inspect the lot?", True, ["hold"], True),
    ("O3", "What torque should the chuck mounting bolts be tightened to?", True, ["110"], True),
    ("O4", "Which oil is used when the TX-200 hydraulic oil is replaced every year?", True, ["46"], True),
    ("R1", "Where do we keep rejected incoming material?", True, ["Q1", "!Red Bin"], True, "Rev 03"),
    ("R2", "Which form do we use to record incoming inspection results?", True, ["QF-07A"], True),
    ("O5", "What is the maximum spindle speed of the TX-200?", False, [], True),
    ("X1", "What is the canteen menu today?", False, [], False),
]

chunks, _ = rag.build_index()
print("doc_no | rev | section | heading | page | chars")
for c in chunks:
    print(f"{c['doc_no']} | {c['rev']} | {c['section']} | {c['heading']} | {c['page']} | {len(c['text'])}")

failed = False
for qid, question, want_found, words, required, *rest in QUESTIONS:
    print(f"\n{qid} {question}")
    for chunk, score in rag.retrieve(question):
        print(f"  {score:.3f} {chunk['doc_no']} Rev {chunk['rev']} S{chunk['section']} {chunk['heading']}")
    result = rag.answer(question)
    answer = result["answer"].lower()
    ok = result["found"] == want_found and all((w[1:].lower() not in answer) if w[0] == "!" else (w.lower() in answer) for w in words)
    if rest:
        ok &= rest[0].lower() in (result["notice"] or "").lower()
    print(f"  found={result['found']} sources={[(s['doc_no'], s['rev'], s['section']) for s in result['sources']]}")
    if result["notice"]:
        print(f"  notice: {result['notice']}")
    print("  " + result["answer"].replace("\n", "\n  "))
    print(f"  {'PASS' if ok else 'FAIL'}{'' if required else ' (not required)'}")
    failed |= required and not ok

sys.exit(1 if failed else 0)
