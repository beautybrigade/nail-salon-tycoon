# Handoff: end of round 3

For a fresh session starting round 4. Read these first: `CLAUDE.md` (standing
rules), `problem.md` (requirements), `spec.md` (how each one is met), and
`docs/decisions/` (0001–0005). This file covers only what they don't.
`handoff-round-2.md` is still here for history. Its warnings that apply to every
session are now in `CLAUDE.md`.

## Current state

- R1–R6 (round 1: terminal game), R7–R8 (round 2: browser game with
  animation), and the round 3 work are implemented:
  - **R9:** the rules are shown before the day begins, and the day starts only
    when the player chooses to begin.
  - **R3 changed:** pedicures get a foot-washing step, with its own animation in
    the browser.
- `python3 -m pytest`: **111 passed** in about 1 second. Round 2 ended with 84;
  round 3 added 27 (16 in `test_r3_foot_washing.py`, 11 in `test_r9_rules.py`)
  and changed 2 existing tests (see decision 0005).
- When this file was written, every round 3 change was committed. This file and
  the round 3 `CLAUDE.md` edit are not committed yet, because the student wants
  to read them first.
- Round 3 commits, oldest first:
  - `5e13c11` round 3 requirements added to `problem.md` (by the student)
  - `9b58534` spec: round 3, with the student's answers
  - `91c2ffe` failing tests for R9 and the R3 change (written before the code)
  - `f9b78c8` salon.py: `Step.WASH_FEET` and `rules()`
  - `f301b52` game.py: prints the rules, waits for Enter, foot-wash message
  - `70111b3` rules(): put the washing step names in quotes
  - `bd078c2` web.py: the `wash-feet` animation name and `GET /api/rules`
  - `9a75be1` static/: rules screen with a Begin button, and the foot-bath animation
  - `ce24ecf` decision record 0004 and README updates
  - `286fdfd` decision record 0005

### What changed in each file this round

| File | Round 3 change |
|------|----------------|
| `salon.py` | `Step.WASH_FEET` ("Wash feet in foot bath"). `required_steps()` adds a washing step before each area (hands → `WASH_HANDS`, feet → `WASH_FEET`). `RuleSection` and `rules()` build the rules text from the game's constants. |
| `game.py` | `print_rules()`, then "Press Enter to begin the day...". Prints "The client's feet soak in the warm foot bath." The step menu now has 8 entries. |
| `web.py` | `GET /api/rules` (`rules_json()`), and `wash-feet` in `STEP_ANIMATIONS`. |
| `static/index.html` | The rules window (`#rules`, `#rules-body`, `#begin` button) and the `#foot-bath` SVG group. |
| `static/app.js` | `showRules()` and `beginDay()`, plus the `wash-feet` entry in `ANIMATIONS` (2600 ms). |
| `static/style.css` | `@keyframes wash-feet` (2.6 s), `foot-ripple`, and the rules window styles. |
| `tests/test_r9_rules.py` | What the rules say, that they follow the constants, the endpoint, and the terminal flow. |
| `tests/test_r3_foot_washing.py` | Where `WASH_FEET` goes for each service, what happens when it is missing, extra, or in the wrong place, and the animation name. |

## How to run

From this folder (`Final Project/nail-salon-tycoon`):

```bash
python3 web.py              # browser game; opens the default browser, Ctrl+C to stop
python3 web.py --seed 42    # same day every time; also --port N, --no-browser
python3 game.py             # terminal game (also takes --seed)
python3 -m pytest           # all tests
```

You need Python 3.10 or newer. It was developed on 3.13.7. pytest is the only
tool outside the standard library.

## Decisions made in round 3 and why

**Answered by the student** (marked **(student)** in spec.md):

- The rules screen shows the **full correct step order**, not just a summary.
- Foot washing is a **required, judged step**, the same as hand washing. It is
  not an automatic animation and not an optional step (decision 0005).
- In a combo, the feet are washed **after the hands are polished**, just before
  the work on the feet starts.
- **Both versions** get the new step: terminal and browser.

**Made by the assistant.** The spec lists these without (student). Revisit any
you disagree with:

1. **The rules text is written once, in `salon.rules()`,** built from the same
   prices, hours, goal, and `Step` labels the game uses (decision 0004). The
   terminal prints it and the browser fetches it. This keeps the text from
   going out of date, and it follows the rule that no game rule lives in
   JavaScript. A test checks that changing the goal changes the rules.
2. **Browser:** the rules appear in a window over the salon with a **Begin the
   day** button. No game is created on the server until Begin is pressed, so
   the day really starts only when the player chooses (R9).
3. **"Play another day" skips the rules** and goes straight to a new day. The
   player has already read them.
4. **Terminal:** the rules are printed, followed by "Press Enter to begin the day...".
5. **The foot-bath animation:** blue water rises around the foot, ripples and
   bubbles, then drains. It is named `wash-feet`, separate from `wash-hands`,
   and like hand washing it doesn't change the nails.
6. **A foot wash at the wrong time still animates** on whichever area is on
   screen and is judged only at Finish. This is the same "show what you did,
   judge at the end" rule as round 2.
7. **The menu was renumbered** to make room for the new step: "Wash feet in
   foot bath" is step 3, so Remove product through Finish moved down by one.
8. **The step names are in quotes** in the rules line about washing, so it
   reads clearly (`70111b3`).
9. **Adding `WASH_FEET` added no new random draw,** so a given `--seed` gives
   the same clients as in round 2. Only the correct steps for pedicures and
   combos changed.

## Unresolved

- The student played round 3 end to end in a real browser: the rules window, Begin button, and foot-bath animation all work.
- **README is a little out of date.** Its file list says `tests/` has "one test
  file per requirement (R1–R8)". There are now R1–R9, and R3 has two files
  (`test_r3_hand_washing.py`, `test_r3_foot_washing.py`).
- **R2 health answers still change nothing.** The client's condition (for
  example "allergic to acetone") is shown for information only. It is a natural
  place for a future requirement, but nobody has asked for it yet.
- Left over from round 2, still true:
  - `game.py` runs its own loop instead of using `salon.Game`, so there are two
    ways of walking through a day.
  - The server never forgets finished games (`SalonServer.games` only grows).
    This is harmless for one player on one computer.
  - A white band at the top during animations was seen only in headless
    screenshots, never in a real browser.

## Warnings for the next session

- **Two lines in `problem.md` describe R3.** The original R3 line still says
  washing is "not needed for pedicures", followed by "(changed in round 3)".
  The "R3 changes" line under Round 3 replaces it for pedicures. Read them
  together, and don't edit `problem.md` (it belongs to the student). The
  current R3 behavior is in spec.md.
- **Adding or reordering a step breaks tests that write out exact
  sequences.** In round 3, two tests in `tests/test_r4_steps.py` had to be
  updated (decision 0005 explains why the others didn't). Tests built from
  `required_steps()` adjust by themselves.
- **The rules window depends on the shape of the text `rules()` returns.**
  `showRules()` in `app.js` styles a line as numbered when it starts with
  `1.` or `a.`, and indents lines that start with spaces. If you change those
  prefixes or the indentation in `salon.rules()`, the browser layout changes
  too. Check it in a browser, not just with pytest.
- **The tests can't see JavaScript or CSS.** They check that animation names
  exist in each file, but not that the rules window or the foot bath look
  right. The headless Chrome screenshot command in `handoff-round-2.md` still
  works for a quick look. For timing and clicks, ask the student to play it.
- **A new step changes the menu numbers again.** Players and any written
  instructions that refer to "step 5" will be wrong. The terminal and the
  browser both build their menus from `Step`, so the code stays consistent.
