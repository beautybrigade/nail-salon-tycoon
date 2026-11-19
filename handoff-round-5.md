# Handoff: end of round 5

For a fresh session starting round 6. Read these first: `CLAUDE.md` (standing
rules, now 1–10), `problem.md` (requirements), `spec.md` (how each one is
met), and `docs/decisions/` (0001–0007). This file covers only what they
don't. The handoffs for rounds 2–4 are still here for history.

## Current state

- All requirements so far are implemented:
  - R1–R6 (round 1): the terminal game.
  - R7–R8 (round 2): the browser game with animation.
  - R9 and the R3 change (round 3): the rules screen and foot washing.
  - R10–R11 (round 4): cuticle nipping, skipped for diabetic clients.
  - Round 5: R12 and R13, below.
- **R12:** a new step, **Pick polish color**, comes right after Buff and right
  before Polish. The player chooses one of the 8 colors on the polish wall. A
  wrong color, a missing pick, a pick in the wrong place, or a second pick
  in a combo means no star. A combo picks **once**, before the hands' Polish,
  and the feet use the same bottle.
- **R13:** manicure and combo clients have a nail shape (square, round,
  stiletto, almond). **File asks for the shape** when the hands are being
  worked on. There is no separate shaping step; this was the student's
  choice. File on the feet asks nothing. A wrong shape means no star.
- Wrong colors and shapes **show on the nails** (student's choice); they are
  judged only at Finish, as before.
- `python3 -m pytest`: **259 passed** in about 2 seconds. Round 4 ended with
  156. Round 5 added 103 tests (`test_r12_polish_color.py`,
  `test_r13_nail_shape.py`) and changed 16 existing ones (listed in decision
  0007).
- Every round 5 change is committed except this file and the `CLAUDE.md`
  edit (rule 10). The student wants to read those two first.
- Round 5 commits, oldest first:
  - `016c6e8` round 5 requirements added to `problem.md` (by the student)
  - `ad33371` spec: round 5, with the student's answers
  - `fd0e29c` failing tests for R12 and R13, plus the updated earlier tests
  - `b651575` salon.py: `Pick`, `Step.PICK_COLOR`, `NAIL_SHAPES`,
    `choices_for()`, `brush_color()`, shapes in the nail look, rules text
  - `89c629d` game.py: color and shape questions in the terminal
  - `294fe6a` web.py: the "choose" reply, `brush_hex`, shapes in the JSON
    (and 3 R7 tests that only broke once web.py changed)
  - `3f735d7` static/: polish wall, chooser pop-up, shape outlines,
    `pick-color` animation, button 9 color
  - `99d8a6f` README
  - `a2b5e4e` decision record 0007

### What changed in each file this round

| File | Round 5 change |
|------|----------------|
| `salon.py` | `NAIL_SHAPES`. `Step.PICK_COLOR` ("Pick polish color") between `BUFF` and `POLISH`. New `Pick(step, choice)` dataclass and the alias `Move = Step \| Pick`. Helpers `step_of(move)` and `move_label(move)` (shows e.g. "File (almond)"). `Client.nail_shape` (default `None`). `_random_client()` draws a shape after the color, only for hand services. `required_steps()` now returns `list[Move]`: `Pick(FILE, shape)` for the hands, plain `FILE` for the feet, `Pick(PICK_COLOR, color)` before the first Polish only. `choices_for(client, steps, step)` returns the options, or `()`. `brush_color()` gives the latest picked color, or the client's color if nothing was picked yet. `NailLook.shape` (default `None`). `Game.choices_for()`, and `Game.take_step(step, choice=None)`, which raises `ValueError` for a missing, unknown, or unwanted choice and also accepts a `Pick`. Rules lines c, d, e. |
| `game.py` | `describe_client()` adds "Wants <color> polish and <shape> nails." `ask_option()` and the `QUESTIONS` dict. `run_service()` asks when `choices_for()` returns options, and prints the bottle or shape line. "Steps so far" and "correct steps" use `move_label()`. |
| `web.py` | `STEP_ANIMATIONS[PICK_COLOR] = "pick-color"`. `look_json()` has `shape`, and `client_json()` has `nail_shape`. `choose_json()`. In `/api/step`, a step that needs a choice and was sent without one returns `{"choose": {step, kind, question, options}}` and takes no step. Step replies have `brush_hex`. `steps_taken` and `correct_steps` use `move_label()`. |
| `static/index.html` | `#polish-wall` (shelves; `.wall-bottles` is filled by JS) and `#picked-bottle`. |
| `static/app.js` | `pick-color` in `ANIMATIONS` (1200 ms). `SHAPE_PATHS` draws the 4 shapes, one `.shaped.shape-<name>` path per hand nail (not toes). `clearShape()`, called in `showNails()` and `renderClient()`. `fillWall()`. `askChoice()` (the pop-up, with Cancel) and `shapeIcon()`. `takeStep()` handles the `choose` reply and sends the choice. `playStep()` sets `--polish` from `reply.brush_hex`, not from the client's color. The client card shows the shape. |
| `static/style.css` | Shape visibility rules. `@keyframes pick-color` (1.2 s) and `polish-wall-show`. `.choices` pop-up styles. `nth-child(9)` button color. |
| `tests/` | New `test_r12_polish_color.py` and `test_r13_nail_shape.py`. `helpers.make_client()` takes `shape=` and gives hand services "almond" by default. Earlier tests changed in r3_foot (1), r4 (3), r7 (3), r8 (1), r10 (3), and r11 (5). |
| `README.md` | Shape and color steps. The test list now says R1–R13. |

## How to run

From this folder (`Final Project/nail-salon-tycoon`):

```bash
python3 web.py              # browser game; opens the default browser, Ctrl+C to stop
python3 web.py --seed 2     # same day every time; also --port N, --no-browser
python3 game.py             # terminal game (also takes --seed)
python3 -m pytest           # all tests
```

You need Python 3.10 or newer (`Step | Pick` at module level needs it). It
was developed on 3.13.7. pytest is the only tool outside the standard library.
**Round 5 added a random draw (the shape), so a seed gives a different day
than in round 4.** `--seed 2` now starts with a manicure (Tangerine,
stiletto, old polish on), which is handy for checking both new steps.

## Decisions made in round 5 and why

**Answered by the student** (marked **(student)** in spec.md):

- **Picking the color is its own step,** judged like the others. R12 says the
  pick happens "right before selecting the polish step", which describes
  a separate action.
- **File asks for the shape** instead of a separate "Shape nails" step.
  Shaping is part of filing, so "right before the filing step" is
  satisfied inside File.
- **A combo picks the color once,** before the hands. The feet use the same
  bottle.
- **The nails show what the player picked,** right or wrong. This is the
  round 2 "show what you did, judge at the end" style.

**Made by the assistant.** The spec lists these without (student). Revisit
any you disagree with:

1. **Choices live in the sequence as `Pick` objects** (decision 0007), so
   one comparison judges everything and "correct steps" shows the answer.
2. **The server decides when to ask** (`choices_for()`). The terminal and
   the page only show the question. The page makes two requests for such
   steps: the first gets `choose`, the second sends the choice. Cancel
   takes no step.
3. **Polish with no pick yet paints the client's own color.** It's still a
   mistake at Finish. This kept round 2's look tests valid. With several
   picks, the latest one is painted.
4. **The wall always offers all 8 colors,** even where a pick is a mistake
   (the combo's feet). Hiding it would give away the answer.
5. **These are mistakes:** a plain File on the hands, a shaped File on the
   feet, and a pick without a color. `Game.take_step` and the server refuse
   choices that aren't offered (the server answers 400).
6. **The shape draw comes after the color draw, only for hand services.**
   This is why seeds changed.
7. **Names and text:** the label is "Pick polish color", the enum is
   `PICK_COLOR`, and the animation is `pick-color` (1.2 s). It's menu step
   8, so Polish is 9 and Finish is 10. Terminal lines: "You take the
   <color> bottle off the polish wall." and "You file the nails into
   a/an <shape> shape." Rules lines d and e are new.
8. **The terminal now shows the wanted color** (before, only the browser
   did) and the shape.
9. **Drawing choices:**
   - Nails keep their long natural look until filed.
   - Shape outlines exist on hand nails only. Toes filed plainly keep the
     round short tip from round 2.
   - The polish wall appears top-left, and a bottle flies to the table.
   - The bottle and brush now show the picked color.
   - Button 9 is `#d6336c`.
10. **Three R7 tests were changed after the failing-test commit** because
    they only broke once `web.py` changed. They're listed in decision 0007.

## Unresolved

- The student played round 5 in a real browser; the color and shape pop-ups and the new steps work.
- **The chooser pop-up can't be closed with Escape,** only with Cancel or
  by choosing. It shares `#overlay`/`#modal` with the result pop-up.
- **The flying bottle always starts from the middle of the wall,** not from
  the slot of the color that was picked.
- **There's no clear-coat look.** Polishing without a pick shows the
  client's color (decision 3 above), which hides that mistake until Finish.
  If the student wants it visible, the server would need to report "no
  color" and the page would need a clear-polish style.
- Left over from earlier rounds, still true:
  - Diabetic clients are rare (about 1 in 10).
  - "Sensitive skin" and "allergic to acetone" still change nothing.
  - The tools' paths skip the thumb.
  - Ragged cuticles stay after a correct diabetic service.
  - `game.py` runs its own loop instead of `salon.Game`.
  - `SalonServer.games` only grows.
  - The white band appears only in headless screenshots.

## Warnings for the next session

- **A sequence holds both `Step` and `Pick` values.** `steps.index(S.FILE)`
  raises for a hand service, because the hands' File is
  `Pick(FILE, shape)`, and `move.value` fails on a `Pick`. Use
  `salon.step_of(move)` to compare and `salon.move_label(move)` to show.
  `s is S.X` filters still work for steps that never carry a choice.
- **Adding or reordering a step still breaks tests that write out exact
  sequences.** Round 5 changed 16. Search the tests for `S.FILE,`,
  `NailLook(`, and `required_steps(` near `==`.
- **Adding another step with a choice means touching all of these:**
  - `choices_for()` in `salon.py`;
  - the `QUESTIONS` dict in `game.py`, which raises a `KeyError` if a step
    needs a choice but has no question;
  - `choose_json()` in `web.py`, which treats anything that isn't
    `PICK_COLOR` as a shape;
  - `askChoice()` in `app.js`, which only draws bottles or shape icons.
- **Each new nail look still needs three changes:** a `NailLook` field with
  a default, a key in `look_json()`, and a class toggle in `showNails()` that
  is also cleared in `renderClient()`. For the shape, the toggle and clear
  are `clearShape()`.
- **The rules screen is read line by line.** Lines d and e start with
  `   d. ` and `   e. ` so `showRules()` numbers and indents them. Keep that
  shape if you add lines.
- **Node isn't installed,** so `app.js` can't be syntax-checked from the
  command line. Use headless Chrome:
  - Copy `static/` into the scratchpad.
  - Turn off transitions there.
  - Append an async script that calls `beginDay()`, then
    `takeStep(...)`, and clicks the `.choices button` whose text matches.
  - Have it `console.log` the results.
  - Serve it with a script that sets `web.STATIC_DIR` before
    `make_server()`.
  - Run Chrome with `--headless=new --virtual-time-budget=40000
    --enable-logging=stderr --screenshot=...`.

  Animations don't finish in headless mode, so tools can appear faint in
  screenshots. Never edit the real `static/` for this.
- **Menu numbers moved again:** Polish is 9 and Finish is 10. Written
  instructions that say "step 8" now mean Pick polish color.
