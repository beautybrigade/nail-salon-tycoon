# Handoff: end of round 6

For a fresh session starting round 7. Read these first: `CLAUDE.md` (standing
rules, now 1–11), `problem.md` (requirements), `spec.md` (how each one is
met), and `docs/decisions/` (0001–0009). This file covers only what they
don't. The handoffs for rounds 2–5 are still here for history.

## Current state

- All requirements so far are implemented:
  - R1–R6 (round 1): the terminal game.
  - R7–R8 (round 2): the browser game with animation.
  - R9 and the R3 change (round 3): the rules screen and foot washing.
  - R10–R11 (round 4): cuticle nipping, skipped for diabetic clients.
  - R12–R13 (round 5): picking the polish color, filing the nail shape.
  - Round 6: the R5 change, below.
- **R5 change (round 6):** the game counts the player's mistakes as 0, 1,
  or "two or more" (`salon.count_mistakes()`, decision 0008).
  - 0 mistakes: 1 star, full price.
  - Exactly 1: ½ star and half the price ($12.50, $17.50, $27.50).
  - 2 or more: no star, $0.

  One mistake means a single change would make the steps right: one skipped
  step, one extra step, one wrong step (a wrong color or shape counts here),
  or one step moved to another place.
- `python3 -m pytest`: **338 passed** in about 2 seconds. Round 5 ended with
  259. Round 6 added 79 tests in `tests/test_r5_half_star.py` and changed
  5 earlier ones (listed in decision 0008).
- Every round 6 change is committed except this file and the `CLAUDE.md`
  edit (rule 11). The student wants to read those two first.
- Round 6 commits, oldest first:
  - `aa5a42b` round 6 requirements added to `problem.md` (by the student)
  - `392fe6f` spec: round 6, with the student's answers
  - `7ef38e0` failing tests, plus the 5 updated earlier tests
  - `6ba181d` salon.py: `count_mistakes()`, half pay, `Decimal`, `money()`,
    rules text
  - `9ededa7` game.py: half-star message, ★/½/– in the summary, cents
  - `a879d7a` web.py: `number()`, `result_json()`, `mistakes`, `stars_so_far`
  - `0082689` static/: half-star pop-up, `money()` and `starText()` in the
    page
  - `5d2d82d` README
  - `7a4f59f` decision records 0008 and 0009

### What changed in each file this round

| File | Round 6 change |
|------|----------------|
| `salon.py` | Imports `Decimal`. `ServiceResult.stars` and `.earned` are now `Decimal`s, plus a new field `mistakes: int = 0` (0, 1, or 2 for "two or more"). `satisfied` is still true only with 0 mistakes. New `_one_change_away(wanted, taken)` and `count_mistakes(client, steps)`. `finish_service()` pays full, half (`price / 2`), or 0. New `money(amount)` gives "$25" or "$12.50". `DayResult.total` is a `Decimal`, summed from `Decimal(0)`. The "Stars and pay" rules section has 3 lines now (full, one mistake, two or more). |
| `game.py` | `describe_client()` and the goal line use `salon.money()`. `run_service()` prints "The client is partly satisfied: one step was wrong. Half a star! +$12.50" for one mistake, followed by the correct steps. New `STAR_MARKS = {0: "★", 1: "½", 2: "–"}`, keyed by `mistakes`, used by `print_summary()`, which also uses `money()` everywhere. |
| `web.py` | Imports `Decimal`. `number(amount)` turns a `Decimal` into a JSON int (25) or float (12.5). `result_json(result)` holds `satisfied`, `stars`, `earned`, `mistakes`. `day_json()` uses `number()` and adds `mistakes` to each row. `/api/finish` adds `stars_so_far`, and `total_so_far` now comes from `game.day_result().total`. |
| `static/app.js` | `money(amount)` (cents only when needed) and `starText(stars)` (★★½, or – for 0), near the top. Every `$${...}` now goes through `money()`. `state.stars` is set from `done.stars_so_far` instead of being added up on the page. `showResult()` has a third pop-up for `r.mistakes === 1`: a half star, the half pay, and the correct steps. The end-of-day table uses `starText()`. |
| `static/style.css` | `.modal .half-star`: a star with a yellow left half (gradient clipped to the text). |
| `tests/` | New `test_r5_half_star.py` (79 tests). Changed: `test_r5_star.py` (wrong order now swaps two pairs, so it's still a $0 case), `test_r11_diabetes.py`, `test_r12_polish_color.py`, `test_r13_nail_shape.py` (a single mistake now expects half; renamed `..._is_one_mistake...`), `test_r7_browser.py` (the reply has `mistakes`). |
| `README.md` | Half pay in the intro. The test list says R5 has two files. |
| `docs/decisions/` | 0008 (counting mistakes) and 0009 (money as `Decimal`). |

## How to run

From this folder (`Final Project/nail-salon-tycoon`):

```bash
python3 web.py              # browser game; opens the default browser, Ctrl+C to stop
python3 web.py --seed 2     # same day every time; also --port N, --no-browser
python3 game.py             # terminal game (also takes --seed)
python3 -m pytest           # all tests
```

You need Python 3.10 or newer. It was developed on 3.13.7. pytest is the
only tool outside the standard library. **Round 6 added no random draw**,
so seeds give the same days as in round 5. `--seed 2` starts with a
manicure (Tangerine, stiletto, old polish on). Skip one step there to see
half pay ($12.50); skip two to see $0.

## Decisions made in round 6 and why

**Answered by the student** (marked **(student)** in spec.md):

- **Any one mistake counts** for half pay: a skipped, extra, wrong, or
  moved step. Asking "only skipped steps?" was the other option; the
  student chose the broader rule.
- **Safety mistakes count the same.** Skipping the health question, or
  nipping a diabetic client's cuticles, earns half if it is the only
  mistake. The other option was "always $0".
- **Keep the cents.** Half pay is exactly half, not rounded.
- **A combo is one service.** Mistakes add up across the hands and feet:
  one on each = $0.

**Made by the assistant.** The spec lists these without (student). Revisit
any you disagree with:

1. **A moved step is one mistake, however far it moved** (decision 0008).
   The student's answer said "one step in the wrong place", and plain edit
   distance would count that as two. Swapping two steps that are far apart
   (File and Polish) is still two, because two steps moved.
2. **The counter only knows 0, 1, and "two or more"** (it returns 2 for
   anything above 1). Nothing needs more yet.
3. **Money is a `Decimal`** (decision 0009). Prices and the goal stay
   whole-dollar `int`s, so earlier tests still pass (`Decimal(25) == 25`).
4. **"$25" but "$12.50":** cents are shown only when there are cents.
5. **`satisfied` still means 0 mistakes.** A half-star result is
   `satisfied=False, mistakes=1`. Code that shows results branches on
   `mistakes`.
6. **Stars are shown as ★ / ½ / –** in both versions. The terminal
   used `*` and `-` before.
7. **The server sends `stars_so_far`** so the page no longer adds up stars
   (CLAUDE.md rule 2: stars are a rule).
8. **Text and look:** "The client is partly satisfied: one step was wrong.
   Half a star!", and a half-yellow star in the pop-up. Confetti only for a
   full star. The rules line is "With exactly one mistake (one missing,
   extra, wrong, or out-of-place step), you get half a star and half the
   price." plus "Two or more mistakes mean no star and $0."
9. **Five earlier tests changed** (decision 0008). R5's wrong-order test
   was kept as a $0 case by making two mistakes instead of expecting half.
10. **Two decision records** (0008, 0009) instead of the minimum one.

## Unresolved

- The student played round 6 in a real browser; the half-star pop-up, the star counter, and amounts like $12.50 all show correctly.
- **The half star in the pop-up uses `background-clip: text`.** It works in
  current Chrome, Safari, and Firefox. In a very old browser it would show
  as an invisible star (transparent text).
- **The game doesn't say which step was the mistake.** After one mistake
  it shows the whole correct list, as before. Saying "you skipped Buff"
  would need `count_mistakes()` to return what it found, not just a number.
- **Some counts may surprise the student**, for example a far swap being
  two mistakes. Worth checking with them if a requirement touches this.
- **The ★, ½, and – characters in the terminal** look fine on macOS. On
  Windows (Git Bash, the course shell) an old code page could show them as
  `?`. Not tested there.
- Left over from earlier rounds, still true:
  - The chooser pop-up can't be closed with Escape.
  - The flying bottle always starts from the middle of the wall.
  - There's no clear-coat look for polishing without a pick.
  - Diabetic clients are rare (about 1 in 10).
  - "Sensitive skin" and "allergic to acetone" still change nothing.
  - The tools' paths skip the thumb.
  - Ragged cuticles stay after a correct diabetic service.
  - `game.py` runs its own loop instead of `salon.Game`.
  - `SalonServer.games` only grows.
  - The white band appears only in headless screenshots.

## Warnings for the next session

- **Results are `Decimal`, not `int`.** `json.dumps()` fails on a `Decimal`
  ("Object of type Decimal is not JSON serializable"). This broke the full-day
  R7 test mid-round. Any new amount in JSON goes through `web.number()`. See
  CLAUDE.md rule 11.
- **`stars` can be 0.5.** Anything that does `"★" * stars`,
  `range(stars)`, or `if r.stars:` meaning "got a star" is now wrong. Use
  `r.mistakes` (0 / 1 / 2) to branch and `r.satisfied` for "perfect".
- **Single-mistake tests no longer mean $0.** A test that wants a $0
  service must make two or more mistakes (finishing with no steps is the
  simplest). A test that wants "unsatisfied" can still use one mistake,
  because `satisfied` is still false.
- **Adding a step can change counts in `test_r5_half_star.py`.** Most of its
  tests are built from `required_steps()`, so they adapt. But the ones that
  remove `S.BUFF` or `S.ASK_HEALTH`, or swap the first/last two moves,
  assume those steps exist and that the swapped neighbors differ.
- **`count_mistakes()` tries every way to move one step**, roughly
  n³ list comparisons. That's fine for about 16 steps. If sequences get much
  longer (multiple areas, many choices), it may need a smarter check.
- **Rules lines are checked by text.** `test_r5_half_star.py` looks for
  "half a star", "half the price", and "two or more" in `salon.rules()`.
- **Inserting JavaScript through a shell heredoc can be blocked** by Claude
  Code's safety check (the `$` and backticks confuse it). Use the Edit tool
  for `static/` changes.
- **Node still isn't installed.** A quick syntax check for `app.js` that
  works on this Mac:

  ```bash
  osascript -l JavaScript -e 'ObjC.import("Foundation"); new Function($.NSString.stringWithContentsOfFileEncodingError("<full path>/static/app.js", 4, null).js); "ok"'
  ```

  It throws a `SyntaxError` on bad code (checked in round 6). For actually
  playing the page headless, use the Chrome steps in `handoff-round-5.md`.
- **Menu numbers did not change this round:** Pick polish color is 8,
  Polish is 9, Finish is 10.
