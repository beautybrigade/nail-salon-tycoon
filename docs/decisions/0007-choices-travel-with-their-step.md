# 0007: A color or shape choice travels with its step, as a Pick (R12, R13)

Status: accepted (round 5)

In the context of **R12 (pick the client's polish color off the wall, right
after Buff and right before Polish) and R13 (file the hands into the client's
nail shape), where the student chose a new "Pick polish color" step for R12
and chose to have the File step itself ask for the shape for R13**, facing
**a judging rule that compares the player's moves to one exact sequence
(decision 0001), nail looks that replay the player's moves (decision 0003),
a terminal game and a browser game that must both ask the question without
holding any game rule (CLAUDE.md rule 2), and 156 earlier tests that build or
compare lists of `Step` values**, we decided for **a small frozen
dataclass, `Pick(step, choice)`, that stands in the sequence wherever a step
carries a choice: `required_steps()` puts `Pick(FILE, <shape>)` for the hands
and `Pick(PICK_COLOR, <color>)` before the first Polish, while every other
step stays a plain `Step`; `finish_service` still just checks the two lists
are equal, and `salon.choices_for()` tells `game.py` and `web.py` when a step
needs a choice and what the options are**, and neglected **keeping the steps
as plain `Step` values and storing the picked color and shape in separate
fields that `finish_service` checks on its own; adding one enum member per
choice (`FILE_SQUARE`, `FILE_ALMOND`, …, `PICK_CHERRY_RED`, …); and letting
the page and `game.py` decide for themselves when to ask (for example
"always ask for a shape on File")**, to achieve **one judging rule for
everything (a wrong color, a wrong shape, a missing pick and a pick in the
wrong place are all just "not the same sequence"), a "correct steps were"
list that shows the answer, such as "File (almond)", nail looks that know
which shape and color the player actually chose, and a terminal and page
that only ask what the server tells them to**, accepting that **a step in
a sequence can now be either a `Step` or a `Pick`, so code that looks at
the step must use `salon.step_of()` and code that shows it must use
`salon.move_label()`, some earlier tests that compared positions or
labels had to change, and `/api/step` can now answer with a question
instead of taking the step, so the page makes two requests for those
steps.**

## Why the alternatives were not chosen

- **Separate fields for the color and shape.** `finish_service` would need a
  second and third check next to the sequence comparison, and the order rule
  ("right after Buff, right before Polish") would still need a step in the
  sequence. The answer shown after a failed service would not say which
  color or shape was expected unless it was handled separately. A combo,
  with one shape and one pick but two Files, would need its own special
  case.
- **One enum member per choice.** The menu would grow from 9 to about 20
  buttons, or `game.py` and the page would have to group them back
  together, and that grouping is a rule. `POLISH_COLORS` and `NAIL_SHAPES`
  would be written twice, as data and as enum members, and could drift
  apart.
- **The front ends decide when to ask.** Whether File needs a shape depends
  on the area being worked on (hands or feet), and that is a game rule.
  Writing it in `game.py` or `app.js` breaks CLAUDE.md rule 2, and the two
  versions could disagree.

## Tests that had to change

Every client now has a color pick, and every hand service has a shaped
File, so the earlier tests that spell out an exact sequence or the finished
nail look changed. Each still checks the requirement it names:

- `tests/test_r4_steps.py`: the manicure, pedicure, and combo sequences
  (3 tests).
- `tests/test_r3_foot_washing.py`: the pedicure sequence (1 test).
- `tests/test_r10_cuticles.py`: the manicure and combo sequences and the
  "nip comes right after File" check now compare `step_of()` of each move
  (3 tests).
- `tests/test_r11_diabetes.py`: the diabetic manicure and combo sequences,
  the hand-built diabetic pedicure, finding the first File, and the terminal
  test, which now answers the shape question (5 tests).
- `tests/test_r8_animation.py`: the finished manicure look now has
  `shape="almond"` (1 test).
- `tests/test_r7_browser.py`: the full browser day sends each choice, the
  wrong-steps test expects labels like "File (almond)", and the step-reply
  test answers the shape question (3 tests). These were changed after the
  failing-test commit, together with `web.py`.

`tests/helpers.py` now gives every hand-service client the almond shape
unless a test asks for another. The new behavior is checked in
`tests/test_r12_polish_color.py` and `tests/test_r13_nail_shape.py`.
