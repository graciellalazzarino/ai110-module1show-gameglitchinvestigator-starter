# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran it, I got a big red `ImportError: DLL load failed ... An Application Control policy has blocked this file` and the textbox to enter my guess didn't work, then it did. That one turned out to be my Windows security blocking part of pandas, not a bug in the game, so I'm not counting it below. Once it loaded, the game looked normal (title, a box to guess, Submit / New Game buttons, and a Developer Debug Info panel), but my score kept going lower and the hints didn't make sense. I didn't even know what "Secret" meant at first. It's the number you're supposed to guess, and once I compared it to the hints I could see they were lying.

Here are the bugs in the order I found them:

1. **The hints are backwards.** I guessed 100 when the secret was 90 and it said "Go HIGHER!" It should have said go lower. In `check_guess` the messages are swapped: "Too High" shows "📈 Go HIGHER!" and "Too Low" shows "📉 Go LOWER!".
2. **The hints flip back and forth.** I guessed 1500 (secret 90) and it said "Go LOWER," then 850 said "Go HIGHER," then 1000 said "Go LOWER" again, even though every one of those is too high. On every even attempt, `app.py` turns the secret into text (`str(st.session_state.secret)`), so it compares "1500" to "90" like words, and "1" comes before "9". The wrong outcome plus the swapped message makes it accidentally look right half the time.
3. **New Game doesn't reset the score or history.** My new game started with a score of -20 from the last one, and History still had my old guesses (20, 15, 30, 15). The New Game button only resets `attempts` and `secret`, not `score`, `history`, or `status`.
4. **The attempts count is off.** After New Game it said I had 1 attempt left, then told me "Out of attempts!" on that guess. The Debug panel said my score was -40 but the message said -45. The info box and Debug panel are drawn before the guess gets processed, so they're always one step behind, and New Game sets attempts to 0 while a fresh game starts at 1.
5. **New Game is stuck on "Game over."** After I lost, I clicked New Game, typed 80, and it just kept saying "Game over. Start a new game to try again." The New Game code never sets `status` back to `"playing"`, so the game stops every time. I had to refresh the page to play again.
6. **No range check.** It says "Guess a number between 1 and 100," but it accepted 1500, 850, 1000, and 900 and used up my attempts. `parse_guess` only checks that it's a number, not that it's in range. There should be something that says "hey, stick within the range."
7. **The secret ignores the difficulty.** On Easy (range 1 to 20) the secret was 95, and on Hard (range 1 to 50) it was 90 and then 68. New Game uses `random.randint(1, 100)` no matter what difficulty you pick, and the info box always says "1 and 100."
8. **Winning on the first guess only gives 70 points.** On a fresh game (Normal) it said "Attempts left: 7" before I guessed anything (Normal allows 8). I guessed 55 and got it right first try, but the final score was 70. Attempts start at 1 instead of 0, Submit adds 1, and then `update_score` does `100 - 10 * (attempt_number + 1)`, so it counts my first guess like my third.

**Play session trace**

```
Game 1 (Easy, range 1-20)
  Guesses: 20, 15, 30, 15     Secret: 95 (outside Easy range)    Score: -20

Clicked New Game, switched to Hard (range 1-50)
  Secret: 90   Score started at -20 (carried over from Game 1)
  Guess 100  -> "Go HIGHER!"   (should be lower)
  Guess 1500 -> "Go LOWER!"
  Guess 850  -> "Go HIGHER!"   (should be lower)
  Guess 1000 -> "Go LOWER!"
  Guess 900  -> "Go HIGHER!" + "Out of attempts! The secret was 90. Score: -45"
               (info box said 1 attempt left, Debug panel said score -40)

Clicked New Game
  Secret: 68   Attempts: 0   Score: -45   History still had all 9 old guesses
  Guess 80   -> "Game over. Start a new game to try again." (every time)

Refreshed the page, Normal (range 1-100)
  "Attempts left: 7" before any guess
  Secret: 55   Guess 55 -> "🎉 Correct!"  "You won! The secret was 55. Final score: 70"
```

**Bug Reproduction Log**

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guess 100, secret 90 (attempt 1) | "Too High" / go lower hint | "📈 Go HIGHER!" | none |
| Guess 1500, secret 90 (attempt 2) | "Too High" outcome | "Too Low" outcome ("📉 Go LOWER!"), because "1500" vs "90" is compared as text | none |
| Click New Game after a game ending at score -20 | Score resets to 0, history empty | Score still -20, history still shows 20, 15, 30, 15 | none |
| Hard difficulty, guess 900 with "Attempts left: 1" | Guess is processed, then game ends with score shown matching Debug panel | "Out of attempts! ... Score: -45" while Debug panel shows -40 | none |
| Lose a game, click New Game, guess 80 | A new game starts and the guess is checked | "Game over. Start a new game to try again." every time | none |
| Guess 1500 (range 1 to 100) | Message saying guess must be between 1 and 100, no attempt used | Accepted as a normal guess and uses an attempt | none |
| Easy difficulty (range 1 to 20) | Secret between 1 and 20 | Secret was 95 | none |
| Fresh game (Normal), first guess 55 = secret 55 | 8 attempts at start, full points (100) for a first-try win | "Attempts left: 7" at start, final score 70 | none |

---

## 2. How did you use AI as a teammate?

I used Claude (in the Claude Code app) for this whole project. I'd describe what I saw while playing, and it helped me figure out what was actually a bug versus my computer (like the DLL error), explained the code behind each bug, made the fixes, and wrote tests.

**A correct AI suggestion:** I didn't understand why the hints seemed random, since 1500 said "Go LOWER" but 850 said "Go HIGHER" with a secret of 90. Claude explained that on every even attempt `app.py` turned the secret into text with `str(st.session_state.secret)`, so "1500" vs "90" got compared like words ("1" comes before "9"), and that the hint messages were also swapped. Its fix was to always compare real numbers in `check_guess` and fix the messages. I checked it with the new tests (`test_too_high_hint_says_go_lower` and `test_big_guess_compared_as_number_not_text`, which both pass) and by playing again on Normal with a secret of 60. Every hint pointed the right way, and 56 correctly said "Go HIGHER!"

**A suggestion I didn't accept as written:** Before asking for help with the New Game bug, I fixed it myself by adding `st.session_state.status = "playing"` to the New Game button. That stopped the "Game over" loop, but when Claude looked at it, it pointed out that my version was only a partial fix because the score and history still carried over from the last game (my new game had started at -20 with my old guesses still listed). So I didn't keep my fix or the original code as written. It got turned into a `reset_game()` function in `logic_utils.py` that resets attempts, secret, score, status, and history, and uses the difficulty's range. I verified it with `test_reset_game_starts_a_fresh_game_after_losing` and by losing a game and clicking New Game, which reset my score to 0 and let me keep playing.

The AI also made a mistake I had to watch for: its first edit deleted `import random` from `app.py` even though the code still used it to pick the secret. It was caught by searching the file before running the game and put back, which showed me I can't assume an AI edit is right just because it looks clean.

---

## 3. Debugging and testing your fixes

I decided a bug was really fixed when two things were true: a pytest test for that exact case passed, and the live game acted right when I played it. I ran `pytest` and all 7 tests passed (the 3 starter tests plus 4 new ones for my two bugs). One test checks that a guess of 100 with a secret of 90 returns "Too High" and the hint says "Go LOWER", which is the exact input that was broken when I started. Another test sets the game to "lost" with a score of -45 and old history, calls `reset_game`, and checks that status is "playing", score is 0, and history is empty. Claude wrote the tests using the same inputs from my Bug Reproduction Log, so the tests prove the exact bugs I documented are gone.

Playing the fixed game also showed me which bugs are still there. On Normal I ran out of attempts after 7 guesses instead of 8, and a guess of 0 was accepted even though the range is 1 to 100. Those are bugs #4/#8 and #6 from my list, which I didn't fix in this round, so they're not new problems.

---

## 4. What did you learn about Streamlit and state?

Streamlit reruns the whole `app.py` file from top to bottom every time you do anything, like clicking a button or pressing Enter in the textbox (which is why the box says "Press Enter to apply," but that doesn't submit your guess). Normal variables get wiped on every rerun, so anything the game needs to remember, like the secret, score, attempts, and history, has to go in `st.session_state`, which is like the game's memory between reruns. That's also why bugs stick around: when New Game didn't reset `status` or `score`, the old values stayed in session state, so the game kept saying "Game over" and my score started at -20. Refreshing the browser page clears session state completely, which is how I got unstuck. The order also matters, because the Debug panel is drawn before the guess is processed, so it always showed the score one step behind.

---

## 5. Looking ahead: your developer habits

One habit I want to keep is writing a Bug Reproduction Log with the exact input, expected, and actual result, and then using those same inputs as my tests. It made it really clear whether something was fixed. I also want to keep using the Debug panel (or print statements) to compare what the code thinks with what the screen shows.

Next time I would read the code myself first and try to understand what each function does before asking AI to fix it. A lot of what was confusing to me (like what "secret" meant or why the hints flipped) would have made more sense if I'd read `check_guess` first.

This project showed me that AI-generated code can look finished and still be wrong in ways you only catch by actually testing it, and that even the AI fixing the bugs can make mistakes, so I have to check its work too.
