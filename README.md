# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Game purpose:** Glitchy Guesser is a number guessing game built with Streamlit. You pick a difficulty (Easy 1 to 20, Normal 1 to 100, Hard 1 to 50), then guess the secret number. After each guess the game gives a hint to go higher or lower, keeps score, and ends when you guess right or run out of attempts.

**Bugs I found** (full details and the Bug Reproduction Log are in `reflection.md`):

1. Hints were backwards: guessing 100 with a secret of 90 said "Go HIGHER!"
2. Hints flipped back and forth because on even attempts the secret was turned into text, so "1500" vs "90" was compared like words.
3. New Game didn't reset the score or history (my new game started at -20).
4. The attempts count is off by one, and the Debug panel shows the score one step behind.
5. After losing, New Game stayed stuck on "Game over."
6. There's no range check: guesses like 1500 or 0 are accepted.
7. The secret ignores the difficulty (Easy gave a secret of 95).
8. Winning on the first guess only gives 70 points.

**Fixes I applied** (bugs #1, #2, and #5):

- Moved the game logic out of `app.py` into `logic_utils.py` (`get_range_for_difficulty`, `parse_guess`, `check_guess`, `update_score`).
- `check_guess` now always compares numbers and returns just `"Win"`, `"Too High"`, or `"Too Low"`. I removed the code in `app.py` that turned the secret into a string on even attempts.
- Added `get_hint_message` so "Too High" shows "Go LOWER!" and "Too Low" shows "Go HIGHER!"
- Added `reset_game`, which New Game now calls. It resets attempts, score, history, and status back to "playing," and picks the secret from the difficulty's range. This fixes the stuck "Game over" and the carried-over score.
- Added 4 pytest tests for these bugs in `tests/test_game_logic.py`.

**Known bugs still there:** the attempts are off by one (#4 and #8; Normal gives 7 guesses instead of 8), and there's no range check (#6).

## 📸 Demo Walkthrough

A game I played after the fixes (Normal, range 1 to 100, secret 60):

1. Started a new game. The score was 0 and the history was empty.
2. Entered 0 and clicked Submit Guess. The game said "📈 Go HIGHER!", which is correct, but it shouldn't have accepted 0 at all since the range is 1 to 100 (bug #6, not fixed yet).
3. Entered 10, 40, 45, 50, and 55. Each one said "📈 Go HIGHER!" and the score went down by 5 each time.
4. Entered 56. It said "📈 Go HIGHER!", which is still correct. Before the fix, even attempts sometimes gave the opposite hint.
5. The game ended with "Out of attempts! The secret was 60. Score: -35". It ended after 7 guesses instead of 8 because of the attempts bug I didn't fix yet (#4).

## 🧪 Test Results

```
$ pytest
collected 7 items

tests\test_game_logic.py .......                                         [100%]

============================== 7 passed in 0.02s ==============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
