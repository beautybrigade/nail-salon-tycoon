# 0005: Make foot washing a required, judged step for pedicures (R3 changed)

Status: accepted (round 3)

In the context of **the round 3 change to R3, where the student asked that a
pedicure client get "a washing animation similar to the handwashing, but for
pedicures", replacing the round 1 rule that washing was simply "not needed for
pedicures"**, facing **a judging rule that compares the player's steps to one
exact sequence (decision 0001), a hand-washing step that the player already
has to choose and can get wrong, and the student's own answer that foot
washing should be required and judged like hand washing**, we decided for
**a new step, `Step.WASH_FEET` ("Wash feet in foot bath"), that
`required_steps()` puts right after the health question for a pedicure and,
for a combo, once after the hands are polished and before any work on the
feet; the player must pick it, a missing, extra, or misplaced foot wash makes
the client unsatisfied, and the browser plays its own `wash-feet` animation
(a foot bath fills, ripples, and drains) while the terminal prints "The
client's feet soak in the warm foot bath."**, and neglected **playing a foot
bath animation on its own at the start of every pedicure without the player
choosing it or being judged on it; offering "Wash feet" as an optional step
that the player may pick or skip with no effect on the star; and leaving R3
as it was, with no foot washing at all**, to achieve **a game where washing
works the same way for hands and feet, so the player learns that every area
is cleaned before nail work, a change that fits the existing exact-sequence
rule with no new kind of judging, and an animation the player sees because
they chose the step, in both the browser and the terminal**, accepting that
**pedicures and combos are now one step longer and easier to fail, the step
menu grows from 7 to 8 choices so the menu numbers after "Ask client to wash
hands" all shift by one, a player used to round 2 will lose stars until they
learn the new step, and earlier tests that spelled out the exact pedicure and
combo sequences had to be rewritten.**

## Why the alternatives were not chosen

- **Automatic animation, not judged.** This would show the foot bath, which is
  what R3 literally asks for, but the player would never decide anything. The
  student wanted foot washing to work like hand washing, and hand washing is a
  step the player must remember. It would also make the browser and terminal
  differ: an animation with no step behind it has nothing to show in the
  terminal.
- **Optional step, not judged.** Every other step either is required or is a
  mistake (decision 0001). A step that never affects the star would be the one
  exception to that rule, it would need special handling in `finish_service`,
  and it would teach the player nothing, since skipping it costs nothing.
- **Leave R3 unchanged.** The student changed the requirement in `problem.md`,
  and requirements belong to the student, so keeping the old rule was not
  really open. It is listed because it was the starting point.

## Tests that had to change

Writing the round 3 tests first (commit `91c2ffe`) meant changing two tests in
`tests/test_r4_steps.py`. Both state the exact correct sequence for a client,
so they were wrong as soon as the correct sequence gained a step:

- `test_r4_pedicure_with_product_starts_with_removal` now expects
  `WASH_FEET` between `ASK_HEALTH` and `REMOVE_PRODUCT`. The test still
  checks the R4 rule it names (removal comes before filing); only the expected
  list changed.
- `test_r4_combo_with_product_does_both_areas_in_order` now expects
  `WASH_FEET` between the hands' `POLISH` and the feet's `REMOVE_PRODUCT`.

No other earlier test had to change, for these reasons:

- The round 1 hand-washing tests (`tests/test_r3_hand_washing.py`) check
  positions in `required_steps()` or insert `WASH_HANDS` into it, so they
  follow the new sequence by themselves. "Pedicure does not require hand
  washing" is still true.
- The R8 nail-look tests pass step lists without `WASH_FEET`, and that is
  fine: washing does not change the nails (decision 0003), so the looks are
  the same with or without it.
- The R5 and R6 tests build their steps from `required_steps()`, so they pick
  up the new step automatically.

The new behavior is checked in `tests/test_r3_foot_washing.py` (16 tests).
