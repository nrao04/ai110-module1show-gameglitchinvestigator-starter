# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game, it felt basically unwinnable because the “Higher/Lower” hint direction didn’t match the secret number I could see in the Developer Debug Info tab. The biggest bug was that the secret was sometimes being treated like a string instead of a number, so the comparisons ended up happening lexicographically (which can flip the hint). I also had issues with the Streamlit session-state setup/reset (like the attempts counter not starting the way I expected and reset logic needing to be tied to the selected difficulty).

---

## 2. How did you use AI as a teammate?

I used Copilot as a teammate while debugging this project. I used it mostly to understand why Streamlit reruns the script on every button click and how to keep key variables from resetting by initializing them in `st.session_state`. One correct suggestion was to gate initialization so `secret`, `attempts`, and `history` are set once (or when difficulty changes / “New Game” is pressed), and then remain stable across submits; I verified it by watching the debug tab while making multiple guesses. One misleading suggestion was framing `check_guess` as returning both an outcome and a message—when I ran `pytest`, it failed because the tests expected only the outcome string, so I adjusted the function contract and confirmed the fix by rerunning tests.

---

## 3. Debugging and testing your fixes
I decided a bug was fixed when the hints matched the numeric relationship between the guess and the secret shown in the debug panel. For testing, I ran `pytest` and used the failures as feedback on the function contract (return types/what the tests were asserting). I also manually tried a couple of controlled guesses in the UI—once `check_guess` compared numbers consistently, the “Too High/Too Low” direction made sense and the game became winnable.

---

## 4. What did you learn about Streamlit and state?

Streamlit reruns the whole script top-to-bottom on every interaction, so normal local variables reset unless you persist them. `st.session_state` is the place to store values that must survive reruns for a single user (like the secret number and attempt count). The key is deciding when to reset that state—when difficulty changes or “New Game” is pressed, `secret` and counters need to reinitialize, otherwise the UI can reflect stale values.

---

## 5. Looking ahead: your developer habits
A habit I want to reuse is treating tests as a contract first: I refactored the logic into `logic_utils.py` and kept iterating until `pytest` passed. Next time, I want to be more explicit with AI about expected inputs/outputs (return types, exact strings, and edge cases) instead of assuming the generated interface will match the tests. This project changed how I think about AI-generated code because I stopped treating it as “production-ready” and started treating it as a starting point that still needs verification and consistent behavior.
