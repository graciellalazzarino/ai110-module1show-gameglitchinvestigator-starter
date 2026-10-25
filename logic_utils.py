import random


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


# FIX: Bug #1 (backwards hints). Claude Code moved check_guess here from app.py.
# The old version returned "Go HIGHER!" for "Too High", and app.py turned the
# secret into a string on even attempts, so "1500" vs "90" was compared like
# words. Now it only compares numbers and returns just the outcome, which is
# what the starter tests in tests/test_game_logic.py expect.
def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome.

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


# FIX: Bug #1. The hint text now matches the outcome: too high means go lower.
def get_hint_message(outcome: str):
    """Return the hint message to show the player for an outcome."""
    if outcome == "Win":
        return "🎉 Correct!"
    if outcome == "Too High":
        return "📉 Go LOWER!"
    return "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


# FIX: Bug #5 (New Game stuck on "Game over"). Claude Code pulled the New Game
# reset out of app.py so it can be tested. The old button only reset attempts
# and secret, so status stayed "lost" and the score and history carried over.
def reset_game(state, low: int, high: int):
    """Reset the game state for a new game within the range low to high."""
    state["attempts"] = 0
    state["secret"] = random.randint(low, high)
    state["score"] = 0
    state["status"] = "playing"
    state["history"] = []
