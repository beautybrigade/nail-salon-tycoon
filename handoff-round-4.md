# Handoff: end of round 4

For a fresh session starting round 5. Read these first: `CLAUDE.md` (standing
rules, now 1–9), `problem.md` (requirements), `spec.md` (how each one is met),
and `docs/decisions/` (0001–0006). This file covers only what they don't.
`handoff-round-2.md` and `handoff-round-3.md` are still here for history.

## Current state

- All requirements so far are implemented:
  - R1–R6 (round 1): the terminal game.
  - R7–R8 (round 2): the browser game with animation.
  - R9 and the R3 change (round 3): the rules screen and foot washing.
  - Round 4: R10 and R11, below.
- **R10:** a new step, **Nip cuticles**, comes right after File and right
  before Buff, once per area. A combo nips both hands and feet.
- **R11:** for a client whose health condition is diabetes, nipping is left
  out of the correct sequence. Nipping that client anyway is a mistake: no
  star, $0 (decision 0006).
- `python3 -m pytest`: **156 passed** in about 1 second. Round 3 ended with
  111. Round 4 added 45 tests (26 in `test_r10_cuticles.py`, 19 in
  `test_r11_diabetes.py`) and changed 6 existing ones (listed in decision
  0006).
- Every round 4 change is committed except this file and the `CLAUDE.md`
  edit (rule 9). The student wants to read those two first.
- Round 4 commits, oldest first:
  - `19c7eb3` round 4 requirements added to `problem.md` (by the student)
  - `570a924` spec: round 4, with the student's answers
  - `631294d` failing tests for R10 and R11, plus the 6 updated earlier tests
  - `ea96d43` salon.py: `Step.NIP_CUTICLES`, the diabetes exception,
    `NailLook.cuticles_nipped`, and the rules text
  - `356a13e` game.py: terminal message for nipping
  - `4b80ce9` web.py: the `nip-cuticles` animation name and `cuticles_nipped`
    in the JSON
  - `0ab5023` static/: cuticles on every nail, the nippers animation, and
    colors for step buttons 7 and 8
  - `bed2cd4` README updates
  - `979957d` decision record 0006

### What changed in each file this round

| File | Round 4 change |
|------|----------------|
| `salon.py` | `DIABETES` constant (used in `HEALTH_CONDITIONS`). `Step.NIP_CUTICLES` ("Nip cuticles"), placed between `FILE` and `BUFF` in the enum, so it is also the menu order. `required_steps()` adds it after each `FILE` unless `health_condition == DIABETES`. `NailLook.cuticles_nipped: bool = False`. `nail_looks()` now uses `dataclasses.replace`. In `rules()`, line c reads "File, then Nip cuticles, then Buff, then Polish. Never nip the cuticles of a client with diabetes." |
| `game.py` | Prints "  You carefully nip the cuticles." The menu now has 8 steps plus Finish (9). |
| `web.py` | `STEP_ANIMATIONS[NIP_CUTICLES] = "nip-cuticles"`, and `"cuticles_nipped"` in `look_json()`. |
| `static/index.html` | The `#nippers` SVG tool (two `.blade` groups around a pivot at 0,0). |
| `static/app.js` | `nip-cuticles` in `ANIMATIONS` (1800 ms, `changeAt: 0.5`). `raggedEdge()`. Every nail now has a `.cuticle.ragged` path and a `.cuticle.neat` path. `showNails()` sets the `nipped` class, and `renderClient()` clears it. |
| `static/style.css` | `.cuticle` styles. `@keyframes nip-cuticles` (1.8 s) moves the tool, and `nipper-snip-l`/`-r` (0.3 s × 5) snip the blades. New `nth-child(7)` and `(8)` button colors. |
| `tests/` | New `test_r10_cuticles.py` and `test_r11_diabetes.py`. Expected sequences updated in `test_r4_steps.py` (3 tests), `test_r3_foot_washing.py` (2), and `test_r8_animation.py` (1). |
| `README.md` | Nipping and the diabetes rule. The test list now says R1–R11. |

## How to run

From this folder (`Final Project/nail-salon-tycoon`):

```bash
python3 web.py              # browser game; opens the default browser, Ctrl+C to stop
python3 web.py --seed 42    # same day every time; also --port N, --no-browser
python3 game.py             # terminal game (also takes --seed)
python3 -m pytest           # all tests
```

You need Python 3.10 or newer. It was developed on 3.13.7. pytest is the only
tool outside the standard library. Round 4 added no new random draw, so a
given seed gives the same clients as in rounds 2 and 3.

## Decisions made in round 4 and why

**Answered by the student** (marked **(student)** in spec.md):

- **Nipping a diabetic client is a mistake** (no star), not an optional step.
  It fits the exact-sequence judging and teaches the real safety lesson
  (decision 0006).
- **A combo nips both areas**, hands and feet, like every other nail step.
- **The nails change after nipping:** ragged cuticles become a neat line, the
  same way File and Buff change the look.

**Made by the assistant.** The spec lists these without (student). Revisit any
you disagree with:

1. **The diabetes exception follows the client's real condition**, not
   whether the player asked. R2 already costs the star if the player doesn't
   ask first, so this never rewards skipping the question, and
   `required_steps()` stays a function of the client alone (decision 0006).
2. **Ragged cuticles are drawn for every client at the start, diabetic ones
   included**, so the picture doesn't give away the health answer. As a
   result, a perfect service on a diabetic client ends with ragged cuticles
   on screen.
3. **Names and text:** the label is "Nip cuticles", the enum is
   `NIP_CUTICLES`, and the animation is `nip-cuticles`. The terminal line is
   "You carefully nip the cuticles." The rules line is quoted under
   `salon.py` above.
4. **Menu position:** "Nip cuticles" is step 6, so Buff, Polish, and Finish
   moved to 7, 8, and 9.
5. **The animation:** pink and purple nippers move along the nail bases at
   y ≈ 286–290 with snipping blades. The nails change halfway through. The
   nipped cuticle is a white curve at 0.9 opacity, made stronger after the
   first pale pink was hard to see on old polish.
6. **Fixed a button-color bug** that was not requested. Only 6
   `nth-child` color rules existed, so Polish (button 7) had been grey since
   round 3, and Buff became grey in round 4. Colors were added for buttons 7
   and 8, and this is now `CLAUDE.md` rule 9.
7. **`cuticles_nipped` defaults to `False`** so the existing `NailLook(...)`
   calls in tests still work. `nail_looks()` was tidied to use `replace()`.
8. **How often diabetes comes up was not changed** (see Unresolved).
9. **Failing tests were committed before the code**, as in round 3.

## Unresolved

- The student played round 4 in a real browser; the nipping step and animation work.
- **Diabetic clients are rare:** about 1 client in 10 (30% of clients have a
  condition, and diabetes is 1 of 3). A whole day can pass without one. If
  the student wants R11 to come up more often, that means changing
  `HEALTH_CONDITION_CHANCE` or the list, and that changes which days each
  seed produces.
- **The other health answers still change nothing.** "Sensitive skin" and
  "allergic to acetone" are shown for information only. An obvious next
  requirement would be for acetone to affect product removal, but nobody has
  asked for it.
- **The nippers skip the thumb.** On the hand, the thumb nail sits higher and
  is rotated, and the nippers' path doesn't reach it. The other tools have
  the same limit.
- **Ragged cuticles stay on screen** after a correct diabetic service
  (decision 2 above). If the student finds that confusing, one option is to
  hide the cuticle lines once the nails are polished. That has to come from
  the server's look, not from JavaScript.
- Left over from earlier rounds, still true:
  - `game.py` runs its own loop instead of using `salon.Game`.
  - `SalonServer.games` only grows, which is harmless for one player.
  - The white band seen only in headless screenshots.

## Warnings for the next session

- **Adding or reordering a step breaks tests that write out exact
  sequences.** Round 4 had to update six. Search the tests for `S.FILE,`
  and for `NailLook(` to find them. Tests built from `required_steps()` adjust
  by themselves.
- **The R11 tests assume the diabetes condition is the string `"diabetes"`**
  (`salon.DIABETES`). Renaming it means updating `HEALTH_CONDITIONS`, the
  constant, and `test_r11_diabetes.py` together. The rules line uses the
  constant, so it follows by itself.
- **The rules text is shown in the browser line by line.** The new line c is
  long but still starts with `   c. `, so `showRules()` still numbers and
  indents it. If you split it into two lines, an indented line without a
  letter shows as a plain indented bullet. Check it in a browser.
- **Headless screenshots don't show animations reliably.** With
  `--virtual-time-budget`, timers advance but CSS animations and transitions
  don't keep pace, so a frame "mid-animation" can show the wrong thing. What
  worked this round:
  - Copy `static/` to a scratch folder.
  - Add CSS there that turns off all transitions and animations and pins a
    tool in place (for example `#nippers { opacity: 1 !important;
    transform: translate(320px, 290px) !important; }`).
  - Append `setTimeout(beginDay, 200); setTimeout(() => takeStep("FILE"),
    400); ...` to the copy of `app.js`.
  - Serve it with a small script that sets `web.STATIC_DIR` to the scratch
    folder before calling `web.make_server()`.

  Never edit the real `static/` for this. For motion and timing, ask the
  student to play.
- **Each new nail look needs three changes:** a field on `NailLook` (give it
  a default so existing tests keep working), a key in `web.look_json()`, and a
  class toggle in `showNails()` plus clearing it in `renderClient()` in
  `app.js`. If you forget the clearing, the look carries over to the next
  client.
- **The menu numbers changed again.** Any written instructions that say
  "step 6" mean Nip cuticles now. In round 3, step 6 was Buff.
