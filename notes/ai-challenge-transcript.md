# AI challenge: full transcript

Tool: Gemini (gemini-3.5-flash-lite), temperature 0.7, two turns in one chat. My messages are shown first, the model's replies after. The user journey from THINKING.md was pasted into the first message (shown as "[user journey pasted]"). Text is unedited except one dash replaced by a semicolon.

### ME
You are a skeptical product manager who has shipped tools for factory shop floors, and also a tired night-shift supervisor who has seen many useless apps. Critique this user journey for an AI copilot that answers questions from plant SOP PDFs. Be blunt. What is unrealistic, what is missing, what would make supervisors ignore it? Give your top 6 points, numbered, short.

[user journey pasted]

### AI
As a product manager who has watched good software die on dirty concrete, and a supervisor who just wants to drink my cold coffee in peace, here is why this journey will fail:

1. **Typing on a phone at 2:30 AM:** I’ve got greasy hands, I’m holding a two-way radio, and I’m stressed. I am not typing "AL-104 what to do" into a tiny mobile screen. If this thing doesn't have instant voice-to-text or a camera scanner for the machine error code, it’s dead on arrival.
2. **Plant Wi-Fi is a black hole:** You think signal reaches behind the 30-ton stamping press in Bay 4? It doesn't. If the app spins for 10 seconds waiting to ping a cloud LLM, I’m throwing my phone in my pocket and going back to the paper binder. 
3. **The PDF Revision Time-Bomb:** Plant documentation is a mess of files named `SOP_final_v2_FINAL.pdf`. If your RAG pipeline accidentally reads a superseded PDF and tells me to use ISO VG 46 instead of 68, I fry a $50k spindle. Guess who QA and plant management blame? Me.
4. **LOTO Liability:** Asking a probabilistic AI about safety lockouts (Scenario C) is an OSHA lawsuit waiting to happen. One hallucinated workaround on Lockout/Tagout procedures and corporate legal will have our heads on spikes. Safety rules belong in concrete logic, not a stochastic chatbot.
5. **Stop making it a "chat":** I don't want a polite AI conversationalist asking me how my shift is going. I want a brutal, direct lookup tool. Give me the exact table or part number immediately. All the conversational fluff is just friction.
6. **Supervisors don't read SOPs for alarms:** At 2:30 AM, nobody checks a manual for an error code; we call Dave in maintenance or we kick the cabinet. Your entire premise assumes people actually read SOPs on the night shift; they don't, they rely on tribal knowledge until things break.

### ME
Push back on my main bet: I think showing the source document and revision under every answer is enough for the supervisor to trust it. Is it? And of all the risks, which ONE should a 5 hour prototype fix first?

### AI
**No, citations are not enough.** 

At 2:30 AM, I am not tapping a citation, opening a PDF on my phone, and pinch-zooming to verify page 4 while an operator stares at me. If the answer on the main screen is wrong, a citation just proves the app is *confidently wrong*. Trust isn't built by homework; it's built by never lying to me.

**The ONE thing your 5-hour prototype must fix first:**
Hardcode a ruthless "I Don't Know" fallback. 

If the vector search doesn't hit an exact match above a strict threshold, the app must output *only* this: **"Not found in plant docs. Call Maintenance Extension 402."** 

Do not let the LLM summarize, extrapolate, or guess. The moment it hallucinates a plausible-sounding safety or maintenance procedure to be "helpful," I am deleting the bookmark and telling my team it's garbage.
