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

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
