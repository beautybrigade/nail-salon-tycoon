# Nail Salon Tycoon — standing rules

These rules apply to every session in this project.

1. **Requirements belong to the student.** The requirements in `problem.md` are
   written by the student. The assistant must not change `problem.md`. If a
   requirement looks wrong or unclear, ask the student. Record clarified
   decisions in `spec.md`.
2. **Logic stays separate from terminal I/O.** All game logic lives in
   `salon.py`, which must never call `input()` or `print()`. `game.py` holds
   only the terminal part (menus, prompts, printing) and calls `salon.py`.
   Randomness in `salon.py` comes from a `random.Random` that is passed in, so
   tests can use a seed. The browser version follows the same split:
   `web.py` only serves pages and turns `salon.py` results into JSON, and the
   files in `static/` only draw and animate. No game rule (which steps are
   right, stars, earnings, nail looks, the rules text) may be written in
   JavaScript. The rules screen shows the text from `salon.rules()`, served
   by `GET /api/rules`; don't write rules in `index.html` or `game.py`.
3. **Every test names its requirement.** Each test's name or docstring names
   the requirement ID it checks (for example `R4`). A test must fail if the
   code it checks is wrong.
4. **Standard library only.** No third-party packages, no virtual
   environments, no API keys, logins, or paid services. pytest is the only
   extra tool. Run the tests with `python3 -m pytest`. The browser page uses
   plain HTML, CSS, and JavaScript written in this repository: no CDN links,
   downloaded libraries, or web fonts, so the game works offline.
5. **Never undo or amend a commit.** No `git commit --amend`, `git reset`,
   `git revert` of the student's work, rebases, or force pushes. Fix mistakes
   with a new commit. Do not push; the student pushes.
6. **This folder is its own git repository.** It sits inside the course repo
   (`csc299-main`), where `Final Project/` shows as untracked. Run git
   commands from this folder and commit here, never in the outer repo.
7. **Animation names and durations must match across files.** Each step's
   animation name appears in three places: `STEP_ANIMATIONS` in `web.py`,
   `ANIMATIONS` in `static/app.js`, and `@keyframes` in `static/style.css`.
   Each duration is written twice: `ms` in `app.js` and the `animation:`
   length in `style.css`. Change them together.
8. **Every change applies to both versions.** New steps, rules, and requirements go into both the terminal game (`game.py`) and the browser game, unless the student says otherwise.
9. **Every step button needs its own color rule.** The step buttons get their
   colors from `.steps button:nth-child(N)` rules in `static/style.css`, one
   per button. When a step is added, add a rule for the new last button, or it
   shows up plain grey. (Polish was grey from round 3 until round 4 because of
   this.)
10. **Only `salon.py` decides when a step needs a choice.** A step taken with
    a choice (a polish color, a nail shape) is a `salon.Pick(step, choice)`
    in the sequence; other steps are plain `Step` values. When a step needs
    a choice, and which options to offer, comes only from
    `salon.choices_for()`. `game.py` and `static/` only ask the question
    they are given and never decide when to ask. Code that compares steps
    uses `salon.step_of()`, and code that shows them uses
    `salon.move_label()`.
11. **Money and stars are exact `Decimal`s, worked out only in `salon.py`.**
    Earnings, totals, and stars (1, 0.5, or 0) are `decimal.Decimal`, never
    `float`. Prices and the goal are whole-dollar `int`s. Python code shows
    an amount with `salon.money()` ("$25", "$12.50"). `web.py` sends amounts
    and stars to the page through `web.number()`, because `json` can't
    handle a `Decimal`. The page only writes down the numbers it gets (its
    `money()` and `starText()`) and never works out pay or stars, not even
    halves or sums. To branch on how a service went, use
    `ServiceResult.mistakes` (0, 1, or 2 for "two or more").
