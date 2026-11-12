# THINKING

## Understand the user

### Assumptions
I have not worked in a plant, so these are assumptions built from the four sample documents and general reading about shop-floor roles. I would confirm all of them with the customer.

- The plant is Kaveri Precision Components, Hosur (from the documents). It runs 3 shifts.
- The user is a **shift supervisor** on the shaft machining line (TX-200 CNC machines CNC-04 to CNC-09). The documents also name a "Shift QC Supervisor", who is a close second user.
- Supervisors have a smartphone in their pocket. Tablets may exist at some stations. Plant Wi-Fi works on the floor, but not everywhere.
- Documents live in a QMS system that is easiest to open on an office desktop. Printed copies at machines are marked "uncontrolled" and can be out of date.
- English is fine for reading documents, but the supervisor thinks and talks in Tamil and English mixed.

### Who the supervisor is
- 8 to 15 years on the floor. Started as an operator or technician, has a diploma, got promoted because they know the machines and the people.
- Responsible for one shift: 15 to 25 operators, 6 CNC machines, output target for the shift, safety, and quality of what leaves the line.
- Not the expert on every procedure. They know the common things by heart and look up the rest. The experts (maintenance engineer, QC engineer, safety officer) mostly work the general shift, so at night the supervisor is the most senior person on the floor.

### What they are trying to do during a shift
- Keep machines running and hit the target.
- Make quick calls when something unusual happens: an alarm, a material delivery, a lock left on a machine, an operator asking "can I run this?".
- Make the **correct** call, because a wrong call means scrap, a safety incident, or an audit finding with their name on it.
- Hand over cleanly to the next shift.

### What frustrates them today
- **Finding the answer is slow.** The answer is in a PDF somewhere in the QMS. They have to walk to the office, log in, find the right document, then find the right table. For a 2-minute question this takes 10 to 15 minutes.
- **Not sure which version is current.** Printed copies say "Uncontrolled copy when printed". The sample documents show this exactly: QC-SOP-014 Rev 03 and Rev 04 are both around, and they disagree on sample size, the form to use, and where rejected material goes.
- **Calling someone is the real system.** Today the fastest way is to phone the engineer. At night, nobody picks up, or the supervisor does not want to wake someone up for a "small" question.
- **Answers are buried in tables.** The value they need (coolant 6 to 8 %, torque 110 Nm, OD tolerance +/- 0.050) is one row in a table on page 2.
- **Fear of blame.** If they follow an old procedure or misread a value, they are the one explaining it in the morning meeting.
- **The floor itself.** Noise, gloves, oily hands, standing next to the machine. Long text on a small screen is hard to use.

### What a good tool means for them
Short answer they can act on, from the current document, with the source shown so they can trust it and show it to someone else. If the tool does not know, it should say so clearly instead of guessing.

## User journey

### Scenario A: alarm on a machine at night
1. 2:30 AM. An operator comes to the supervisor: "CNC-06 is showing AL-104, what do I do?"
2. The supervisor takes out their phone and opens the copilot (bookmarked on the home screen, on plant Wi-Fi).
3. They type "AL-104 what to do" (short, maybe with a typo).
4. The app answers in a few seconds: way lube oil level is low, top up with ISO VG 68 to the MAX mark, press RESET, machine can continue. Below the answer it shows the source: MNT-MAN-CNC-02 Rev 02, section 6, page 2.
5. The supervisor reads it, maybe taps the source to see the actual table, and tells the operator what to do.
6. The operator tops up, resets, machine runs. Total time: 2 minutes instead of 15.

What could go wrong:
- The app mixes up oils and says ISO VG 46 (that is the hydraulic oil). The operator puts the wrong oil in the way lube. This is why the source must be shown and why the answer must quote exact values.
- Wi-Fi is weak near the machine, so the answer takes 20 seconds or fails. The supervisor gives up and calls someone.
- The question is about an alarm that is not in the manual (e.g. AL-999). The app must say it does not know, not invent a meaning.
- The answer is too long to read while standing at a noisy machine.

### Scenario B: material arrives at the receiving area
1. A sub-contractor delivers 600 machined BH-220 bearing housings. The QC inspector asks the Shift QC Supervisor how many to check.
2. The supervisor asks the copilot: "600 pieces arrived, how many samples and how many minor defects allowed?"
3. The app answers from QC-SOP-014 **Rev 04**: inspect 32 samples, accept with 1 or fewer minor defects, reject with 2 or more. Any critical defect rejects the whole lot.
4. The inspector then asks "the supplier did not send the test certificate, can we inspect?". The app says no: the lot goes on HOLD until the MTC is received.
5. The supervisor follows the procedure and records it in the QMS app (form QF-07A).

What could go wrong:
- **The app answers from Rev 03** (5 samples for every lot). The lot is accepted after checking 5 pieces instead of 32. Nobody notices until an audit or a customer complaint. This is the biggest risk I found in the sample documents.
- The supervisor still has the old printed Rev 03 at the desk and trusts that over the app. The app needs to show the revision and effective date so the supervisor can see which one is newer.
- The app gives the sampling plan but forgets the "any critical defect = reject the whole lot" rule. A partial answer can be as bad as a wrong one.

### Scenario C: a lock left on a machine
1. Start of shift. CNC-05 has a red lock on it from the maintenance technician of the previous shift, who has gone home.
2. Production wants the machine running. The supervisor asks the copilot: "lock left on machine, owner went home, can I remove it?"
3. The app says: nobody may remove another person's lock. The only exception: the Shift Supervisor tries to phone the owner; if unreachable, the Production Manager and Safety Officer must both authorise, the machine is inspected, removal is recorded on form SF-12, and the owner is informed before their next shift.
4. The supervisor phones the technician first, as the procedure says.

What could go wrong:
- The app answers only "the owner removes their own lock" and skips the absent-owner procedure, so the supervisor thinks they are stuck, or worse, ignores the app and cuts the lock.
- The app sounds too confident on a safety question. For safety answers it should always show the source and ideally remind the user to follow the full procedure.

### Things that apply to every scenario
- **Not in the documents:** the app must say "I could not find this in the plant documents" and point them to a person, instead of making something up. A made-up answer once is enough for the supervisor to stop trusting it forever.
- **Trust:** the supervisor will trust the app only if they can see where the answer came from (document number, revision, page) in one tap.
- **Phone first:** big text, one input box, answer at the top, no login screens in the middle of a shift (for this prototype).
- **Why they would stop using it:** one wrong number, slow answers, or answers that are too long to read standing up.

## AI challenge

I gave the user journey above to Gemini (gemini-3.5-flash-lite) and asked it to act as a skeptical shop-floor product manager and a tired night-shift supervisor. Two turns, key parts below (lightly trimmed).

> **Me:** You are a skeptical product manager who has shipped tools for factory shop floors, and also a tired night-shift supervisor who has seen many useless apps. Critique this user journey [...] Be blunt. What is unrealistic, what is missing, what would make supervisors ignore it? Give your top 6 points.
>
> **AI:**
> 1. **Typing on a phone at 2:30 AM:** I've got greasy hands, I'm holding a two-way radio, and I'm stressed. [...] If this thing doesn't have instant voice-to-text or a camera scanner for the machine error code, it's dead on arrival.
> 2. **Plant Wi-Fi is a black hole:** [...] If the app spins for 10 seconds waiting to ping a cloud LLM, I'm throwing my phone in my pocket and going back to the paper binder.
> 3. **The PDF Revision Time-Bomb:** [...] If your RAG pipeline accidentally reads a superseded PDF [...] Guess who QA and plant management blame? Me.
> 4. **LOTO Liability:** Asking a probabilistic AI about safety lockouts is an OSHA lawsuit waiting to happen. [...] Safety rules belong in concrete logic, not a stochastic chatbot.
> 5. **Stop making it a "chat":** [...] I want a brutal, direct lookup tool. Give me the exact table or part number immediately.
> 6. **Supervisors don't read SOPs for alarms:** At 2:30 AM, nobody checks a manual for an error code. We call Dave in maintenance [...]

> **Me:** Push back on my main bet: I think showing the source document and revision under every answer is enough for the supervisor to trust it. Is it? And of all the risks, which ONE should a 5 hour prototype fix first?
>
> **AI:** **No, citations are not enough.** At 2:30 AM, I am not tapping a citation, opening a PDF on my phone, and pinch-zooming to verify page 4 while an operator stares at me. If the answer on the main screen is wrong, a citation just proves the app is *confidently wrong*. [...] Hardcode a ruthless "I Don't Know" fallback. If the vector search doesn't hit an exact match above a strict threshold, the app must output *only* [a not-found message]. Do not let the LLM summarize, extrapolate, or guess.

### Reflection

**What I agreed with**
- **Citations alone do not create trust.** This was the most useful point. My journey leaned on "show the source and they will trust it". The real trust comes from the app never inventing an answer. So the not-found path is not a nice-to-have: it is two hard guards in code. A similarity threshold refuses clearly off-topic questions without calling the LLM at all, and the LLM must reply with an exact NOT_FOUND token when the excerpts do not contain the answer, which the app turns into a fixed message.
- **It must be a lookup tool, not a chat.** I removed any idea of chat history or greetings. The UI is one input box, the answer first in large text, exact values with units, sources below in a compact line.
- **Speed matters more than I wrote.** I picked a small fast model and keep the search in memory, so an answer comes back in a couple of seconds.
- **The revision time-bomb is real.** It was already in my journey (Scenario B), and the critique confirmed it is the risk with the worst consequence that a prototype can actually fix. This became my improvement.

**What I disagreed with**
- **"Safety rules do not belong in an AI tool."** Partly. The app should not *decide* anything about safety, and it should never invent a workaround. But refusing to answer LOTO questions leaves the supervisor guessing, which is worse. My answer is to quote the procedure as written, include the exceptions and conditions the document states (the absent-owner procedure), and always show the source. The prompt requires that.
- **"Nobody reads SOPs, they call Dave."** True today, and that is exactly the problem. At night Dave is asleep. The tool has to be faster than calling Dave, not compete with a binder. I kept the premise but treat speed as a requirement.
- **Voice and camera input.** Fair point, but out of scope for a 5 hour prototype. Phone keyboards already have a built-in voice dictation button, which works with the text box today. Camera scanning of alarm screens is on my "next" list.
- The AI mixed up two issues in point 3 (ISO VG 46 vs 68 is an oil mix-up between two rows of the same manual, not a revision problem). I keep both as separate risks.

**What I changed**
- Promoted "not found" from a line in the journey to a hard requirement with two guards.
- Made the answer format strict: short, exact values, numbered steps, conditions and safety warnings included, document number named.
- Chose revision awareness as the one improvement (next section).
- Added "faster than phoning someone" as the bar the app has to beat.

The full two-turn conversation is in [notes/ai-challenge-transcript.md](notes/ai-challenge-transcript.md).

## The improvement I added, and why

**Revision-aware answers: the app answers only from the current revision of a document, and warns when an outdated revision also matched the question.**

### Why this one
- It came straight out of my user journey (Scenario B) and the AI challenge both ranked it as a top risk: a supervisor following a superseded procedure is the failure with the worst consequence (wrong sampling, wrong quarantine location, audit finding) and the hardest to notice.
- The sample documents contain exactly this trap. QC-SOP-014 Rev 03 and Rev 04 are both in the folder and they disagree: Rev 03 says check 5 pieces of every lot and put rejects in the Red Bin near Gate 2, Rev 04 says 32 pieces for a 600-piece lot and put rejects in Quarantine Cage Q1. A plain RAG app retrieves both and can blend them.
- Real plants have the same problem: every printed copy says "Uncontrolled copy when printed. Refer to QMS for the latest version", which tells me old copies are everywhere.
- It is small enough to build properly in the time, and easy to verify.

### What it does
1. When the PDFs are loaded, documents with the same document number are grouped, and only the highest revision is marked current. Older revisions are marked "superseded by Rev X (effective date)".
2. Only chunks from current revisions are sent to the model, so the answer cannot come from Rev 03.
3. If a superseded revision ranked among the top matches for the question, the answer carries a **Revision check** notice, for example: "QC-SOP-014 Rev 03 (effective 15-Mar-2023) also matched your question but is superseded by Rev 04 (effective 01-Jul-2026). This answer uses Rev 04 only. Do not use printed Rev 03 copies."
4. Every source in the UI shows the revision, effective date and a **CURRENT** badge.
5. The eval script checks it: the 600-piece lot question must say 32 and show the notice, and "where do we keep rejected material?" must say Cage Q1 and must **not** say Red Bin.

### Why the notice and not just silently using Rev 04
The supervisor may be holding the printed Rev 03. If the app silently says "32 samples" and the paper says "5 samples", they will trust the paper. The notice explains the conflict and tells them which copy to throw away.

### Limits
- "Latest revision number = current" is an assumption. In a real QMS a newer revision can be in draft or not yet effective. The right source of truth is the QMS document status, not the file name.
- Rev 04 also adds new rules that Rev 03 never had (MTC mandatory, 4-hour SQE escalation). The notice does not list what changed; the revision history section of the document does.

## Final reflection

### What I would build next
1. **Connect to the QMS instead of a folder of PDFs**, so "current revision" and "effective date" come from the system of record, and new revisions are picked up automatically.
2. **Feedback on every answer** ("this was wrong / this helped"), logged with the question and sources, so the plant can see what supervisors ask and where the documents or the app fall short.
3. **Voice input and short read-aloud answers** for gloves and noise, and **camera input** to read an alarm code off the machine screen.
4. **Safety-question handling**: detect LOTO and other safety topics and always show the full procedure steps and the "call the safety officer" path, not a summary.
5. **Better page links**: today a source links to the page where the section starts; for long tables it should link to the page with the matching row.
6. **Offline fallback** for dead Wi-Fi zones: cache the last answers and the alarm table on the phone.

### What I am unsure about
- Whether supervisors would really type questions, or would prefer picking from a list of machines and alarms.
- Whether answers should be in Tamil or mixed language for some users.
- How the plant feels about a cloud LLM seeing their documents. A local model would avoid that, but needs hardware.
- How well the similarity threshold scales. It is calibrated on 4 documents and a handful of questions; with hundreds of documents, off-topic questions will match something, and the "not found" behaviour will rely more on the model's NOT_FOUND rule.

### What I would ask the customer
1. Where do the documents live today (QMS name), and can we read revision status and effective dates from it?
2. Who are the first users: production supervisors, QC supervisors, maintenance? Which shift?
3. What phones or tablets do they carry, and how good is Wi-Fi on the floor?
4. Which questions are asked most often today, and who answers them? (These become the test set.)
5. Are there questions the copilot must never answer, or must always escalate (for example, safety overrides)?
6. Can documents leave the plant network for a cloud model, or must everything run on-site?
7. Do supervisors need to show the answer to auditors, and does that need a log?

### Challenges I faced and how I handled them

**Biggest challenge: the LLM API itself, under a deadline.**
- The default model I planned to use (gemini-2.5-flash) was no longer available for new API keys, and the newer flash models returned "overloaded" (503) or timed out when I tested them. I wrote a small script that tried each candidate model once and measured the reply time, then picked gemini-3.5-flash-lite, which answered in about 1 second. I also found that newer models reject the old `thinking_budget` setting and need `thinking_level` instead. The model name is in `.env`, so switching is a one-line change.
- The free tier allows 15 requests per minute. Each question costs one embedding call and one chat call, so running the full test script twice in a row hit the limit. I kept the test set small, ran it once per change, and made the API return a friendly "the AI service is busy, try again in a minute" message instead of a crash.
- My API key stopped working mid-build (I rotated it after it was exposed in a screenshot, and the first replacement I pasted was not a valid key). I checked the key's format without printing it and replaced it. The key is only in a local `.env` that is git-ignored.

**Other challenges**
- **PDF text is messy.** Footers like "QC-SOP-014 | Rev 04 | Uncontrolled copy..." appear in the middle of the extracted text, and numbered procedure steps look exactly like numbered section headings. I chunk by section and only accept a numbered line as a heading if it is the next section number, short, and not a sentence. A printed table of all 28 chunks let me check every split by eye.
- **Two revisions of the same SOP** (see the improvement).
- **Windows setup**: the `python` on my PATH was an MSYS2 build that created a broken virtual environment layout, so I used the standard CPython 3.12 install. Git's line-ending conversion could have corrupted the PDFs on checkout, so I marked `*.pdf` as binary in `.gitattributes`.
- **Opening the app from my phone**: the server has to listen on `0.0.0.0` instead of `127.0.0.1`, and Windows Firewall blocks incoming connections on port 8000 by default. I added an inbound firewall rule for port 8000 on my private network and opened `http://<laptop-ip>:8000` on the phone.
