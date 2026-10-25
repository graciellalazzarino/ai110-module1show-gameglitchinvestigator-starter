from logic_utils import check_guess, get_hint_message, reset_game

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# Bug #1: hints were backwards, and big numbers were compared like text
# ("1500" < "90"). These check the outcome and the hint message match.
def test_too_high_hint_says_go_lower():
    # Guess 100 with secret 90 used to say "Go HIGHER!"
    assert check_guess(100, 90) == "Too High"
    assert "LOWER" in get_hint_message("Too High")


def test_too_low_hint_says_go_higher():
    assert check_guess(10, 90) == "Too Low"
    assert "HIGHER" in get_hint_message("Too Low")


def test_big_guess_compared_as_number_not_text():
    # Guess 1500 with secret 90 used to come back "Too Low" on even attempts
    assert check_guess(1500, 90) == "Too High"


# Bug #5: New Game left status as "lost", so the game said "Game over" forever,
# and the score and history carried over from the last game.
def test_reset_game_starts_a_fresh_game_after_losing():
    state = {
        "attempts": 5,
        "secret": 90,
        "score": -45,
        "status": "lost",
        "history": [100, 1500, 850, 1000, 900],
    }
    reset_game(state, 1, 50)
    assert state["status"] == "playing"
    assert state["attempts"] == 0
    assert state["score"] == 0
    assert state["history"] == []
    assert 1 <= state["secret"] <= 50
