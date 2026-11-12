# Shopfloor Copilot

A phone-friendly copilot for shop-floor supervisors. It answers questions from the plant's SOPs and manuals (4 sample PDFs from a fictional plant, Kaveri Precision Components, Hosur), shows the source document, revision, section and page, says clearly when the answer is not in the documents, and answers only from the current revision of each document.

## What it does

- **Grounded answers with sources.** Every answer lists the document number, revision, section and page it came from. Tapping a source opens that page of the PDF.
- **Says so when it does not know.** Two guards: a similarity threshold (nothing close enough in the documents means no answer is attempted) and a model rule (the model must reply NOT_FOUND if the excerpts do not contain the answer).
- **Revision awareness (the improvement I added).** Only the current revision of each document reaches the model. If an older revision matched the question, the answer shows a "Revision check" notice saying it is superseded. Why I chose this is in the "The improvement I added, and why" section of [THINKING.md](THINKING.md).
- **Phone-first UI.** Built for a supervisor holding a phone; open it from any phone on the same Wi-Fi (see below).
- **Friendly message when the AI service is busy** instead of a raw error.

## How it works

1. Each PDF is read with pypdf and split into section chunks. Every chunk carries the document number, revision, effective date and page.
2. Each chunk is embedded with Gemini embeddings (`gemini-embedding-001`) and kept in memory.
3. A question is embedded and compared with every chunk by cosine similarity. Only chunks from the current revision of each document are kept.
4. If the best match is below the similarity threshold (0.65), the app answers "not found" without calling the model.
5. Otherwise the top excerpts go to Gemini (`gemini-3.5-flash-lite`), which may answer only from those excerpts or reply NOT_FOUND.
6. The answer is shown with its sources, plus a revision notice when a superseded revision also matched.

There is no vector database: four short documents fit comfortably in memory, and the index is rebuilt at startup.

## Setup

Requires Python 3.12. In PowerShell, from the project folder:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and put a Gemini API key (free from https://aistudio.google.com/apikey) in `GEMINI_API_KEY`. The model names (`GEMINI_CHAT_MODEL`, `GEMINI_EMBED_MODEL`) are also set there and can be changed.

On macOS or Linux, activate with `source .venv/bin/activate` and use `python` in place of `.venv\Scripts\python.exe`.

## Run

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000.

## Open it from a phone on the same Wi-Fi

1. Find the laptop's IP address with `ipconfig` (the Wi-Fi adapter's IPv4 address).
2. On the phone, open `http://<laptop-ip>:8000`.

Notes:

- `--host 0.0.0.0` is what makes the app reachable from other devices. Without it only the laptop itself can open it.
- Windows Firewall blocks port 8000 by default. Allow the prompt for private networks when it appears, or run this in an administrator PowerShell:

  ```powershell
  New-NetFirewallRule -DisplayName "Shopfloor Copilot 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private
  ```

  Remove the rule when you are done:

  ```powershell
  Remove-NetFirewallRule -DisplayName "Shopfloor Copilot 8000"
  ```

- If Windows marks the Wi-Fi as Public, either switch it to Private or add `-Profile Public` to the rule.

## Test

```powershell
.venv\Scripts\python.exe eval.py
```

Runs the 5 sample questions, my own 5 questions, revision checks and an off-topic question, printing PASS or FAIL for each. It exits with code 1 if a required check fails. The free tier allows 15 chat requests per minute, so do not run it twice within a minute.

## My 5 questions and the app's answers

Answers below are copied unedited from a run of `eval.py`.

### O1. A lot of 600 pieces arrived. How many samples do we inspect and how many minor defects are allowed?

Found. Sources: QC-SOP-014 Rev 04, section 4 (Sampling Plan).

Revision check: QC-SOP-014 Rev 03 (effective 15-Mar-2023) also matched your question but is superseded by Rev 04 (effective 01-Jul-2026). This answer uses Rev 04 only. Do not use printed Rev 03 copies.

> To determine the number of samples to inspect and the minor defect allowance for a lot of 600 pieces, follow the sampling plan:
>
> 1. Locate the lot size range in the sampling plan: 501 - 3,200 pieces.
> 2. Inspect **32 samples** drawn at random.
> 3. Accept the lot if there are **1 or fewer** minor defects.
> 4. Reject the lot if there are **2 or more** minor defects.
>
> Document QC-SOP-014 Rev 04

### O2. The supplier did not send the material test certificate. Can we still inspect the lot?

Found. Sources: QC-SOP-014 Rev 04, section 5 (Procedure).

Revision check: QC-SOP-014 Rev 03 (effective 15-Mar-2023) also matched your question but is superseded by Rev 04 (effective 01-Jul-2026). This answer uses Rev 04 only. Do not use printed Rev 03 copies.

> No. The Material Test Certificate (MTC) is mandatory. If it is missing, the lot is put on HOLD and must not be inspected or accepted until the MTC is received.
>
> Document: QC-SOP-014 Rev 04

### O3. What torque should the chuck mounting bolts be tightened to?

Found. Sources: MNT-MAN-CNC-02 Rev 02, section 5 (Chuck Mounting Bolt Torque).

> Tighten the chuck mounting bolts to 110 Nm using a calibrated torque wrench in a criss-cross sequence.

### O4. Which oil is used when the TX-200 hydraulic oil is replaced every year?

Found. Sources: MNT-MAN-CNC-02 Rev 02, section 4 (Preventive Maintenance Schedule).

> ISO VG 46
>
> Document: MNT-MAN-CNC-02 Rev 02

### O5. What is the maximum spindle speed of the TX-200?

Not found. No sources.

> I could not find this in the plant documents I have. Please check with your supervisor or the QMS.

The documents only cover spindle runout, not spindle speed, so the app refuses instead of guessing.

## Sample questions (from the assignment)

### S1. What is the recommended coolant concentration for the TX-200 CNC turning centre?

Found. Sources: MNT-MAN-CNC-02 Rev 02, section 3 (Normal Operating Parameters) and section 6 (Common Alarms).

> The recommended coolant concentration is 6 - 8 %.

### S2. The machine is showing alarm AL-104. What does it mean and what should the operator do?

Found. Sources: MNT-MAN-CNC-02 Rev 02, section 6 (Common Alarms).

> Based on Document MNT-MAN-CNC-02 Rev 02:
>
> Meaning: Way lube oil level low.
>
> Operator action:
> 1. Top up with ISO VG 68 oil to the MAX mark.
> 2. Press RESET.
> (Note: Machine can continue after reset.)

### S3. Who is allowed to remove a lockout lock from a machine?

Found. Sources: SAF-SOP-003 Rev 05, section 5 (Removing Locks) and section 6 (Removal of a Lock When the Owner Is Absent).

> Each authorised person removes only their own lock. Nobody may remove another person's lock.
>
> Exception: If an authorised person has left the plant without removing their lock, it may be removed only after the Shift Supervisor attempts to contact the owner by phone, the Production Manager and the Safety Officer both authorise the removal, the machine is physically inspected to confirm it is safe, and the removal is recorded on form SF-12 Lock Removal Record.
>
> Document: SAF-SOP-003 Rev 05

### S4. What is the outer diameter tolerance for the BH-220 bearing housing?

Found. Sources: QC-SOP-014 Rev 04, section 6 (Inspection Dimensions - BH-220 Bearing Housing).

> The outer diameter tolerance for the BH-220 bearing housing is +/- 0.05 mm.

### S5. How often should spindle runout be checked, and who does it?

Found. Sources: MNT-MAN-CNC-02 Rev 02, section 4 (Preventive Maintenance Schedule).

> Spindle runout should be checked monthly by a maintenance technician.

## Project layout

```
app/
  main.py          FastAPI app: POST /api/ask, serves the UI and the PDFs
  rag.py           PDF chunking, embeddings, search, answer generation
  static/
    index.html     phone-first UI
docs/              the 4 plant PDFs (served at /pdfs)
assignment/        the original assignment files
notes/             AI challenge transcript
eval.py            sample, own and revision-check questions with PASS/FAIL
THINKING.md        user research, journey, AI critique, improvement, reflection
requirements.txt   pinned dependencies
.env.example       template for the Gemini key and model names
```

## Limitations

- "Current revision" means the highest revision number found in the documents, not the status in a real quality management system.
- A source link opens the page where the section starts. For a long table that can be one page before the exact row.
- The similarity threshold was calibrated on these 4 documents and would need re-checking on a larger set.
- The free Gemini tier allows 15 chat requests per minute, so the app can report that the AI service is busy.
- Document excerpts are sent to a cloud LLM.
- There is no login and no audit log.

See [THINKING.md](THINKING.md) for user research, the user journey, the AI critique and the final reflection.
