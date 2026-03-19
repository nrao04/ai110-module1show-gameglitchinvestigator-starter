import random
import streamlit as st

from logic_utils import (
    check_guess,
    get_hint_message,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

def get_temperature_hint(guess: int, secret: int) -> str:
    """Return a proximity hint based on distance to the secret."""
    distance = abs(guess - secret)
    if distance == 0:
        return "🎯 Exact match"
    if distance <= 2:
        return "🔥 Very hot"
    if distance <= 5:
        return "🌡️ Warm"
    if distance <= 10:
        return "🧊 Cold"
    return "❄️ Freezing"


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")
show_enhanced_ui = st.sidebar.checkbox("Enhanced UI mode", value=True)
show_temp_hints = st.sidebar.checkbox("Temperature hints", value=True)

if st.session_state.get("game_difficulty") != difficulty:
    # Streamlit reruns the whole script on every interaction; this ensures
    # the game state stays consistent when the user changes difficulty.
    st.session_state.game_difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.history_rows = []

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

if show_enhanced_ui:
    attempts_used = st.session_state.attempts
    attempts_remaining = max(0, attempt_limit - attempts_used)
    progress = min(1.0, attempts_used / attempt_limit)

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Score", st.session_state.score)
    metric_col2.metric("Attempts Used", attempts_used)
    metric_col3.metric("Attempts Left", attempts_remaining)
    st.progress(progress, text=f"Attempts progress: {attempts_used}/{attempt_limit}")

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)
    st.write("History Rows:", st.session_state.get("history_rows", []))

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.history_rows = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.session_state.history_rows.append(
            {
                "Attempt": st.session_state.attempts,
                "Guess": raw_guess,
                "Outcome": "Invalid",
                "Hint": err,
                "Temperature": "-",
            }
        )
        st.error(err)
    else:
        st.session_state.history.append(guess_int)
        outcome = check_guess(guess_int, st.session_state.secret)
        hint_text = get_hint_message(outcome)
        temp_text = (
            get_temperature_hint(guess_int, st.session_state.secret)
            if show_temp_hints
            else "-"
        )

        if show_hint:
            st.warning(hint_text)
            if show_temp_hints and outcome != "Win":
                st.caption(f"Proximity hint: {temp_text}")

        st.session_state.history_rows.append(
            {
                "Attempt": st.session_state.attempts,
                "Guess": guess_int,
                "Outcome": outcome,
                "Hint": hint_text,
                "Temperature": temp_text,
            }
        )

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

if show_enhanced_ui and st.session_state.get("history_rows"):
    st.subheader("Guess History")
    st.dataframe(st.session_state.history_rows, use_container_width=True, hide_index=True)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
