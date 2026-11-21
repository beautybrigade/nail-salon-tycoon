# 0008: Count mistakes as "how many changes make the steps right", with a moved step as one (R5, round 6)

Status: accepted (round 6)

In the context of **the round 6 change to R5, where exactly one mistake
earns half a star and half the price and two or more earn nothing, and the
student's answer that any one mistake counts: one skipped step, one extra
step, one wrong step (including a wrong color or shape), or one step done
in the wrong place**, facing **a judging rule that only knew "exactly
right or not" (decision 0001), sequences that mix `Step` and `Pick` values
(decision 0007), and a player who can do any steps in any order**, we
decided for **a function, `count_mistakes()`, that keeps the one correct
sequence from decision 0001 and asks whether a single change turns the
player's steps into it: removing one step, adding one step, replacing one
step, or moving one step to another place, near or far. It returns 0 for an
exact match, 1 if one such change is enough, and 2 (meaning "two or more")
otherwise**, and neglected **the usual edit distance (Levenshtein: skip,
add, or replace one step, each costing 1), the same with side-by-side swaps
as one change (Damerau), and a list of separate rule checks that each
report a mistake (for example "health asked first", "buff before polish",
"right color")**, to achieve **a count that matches what a player would
call "one mistake", including Polish done before Buff or the health question
asked at the end, one exact sequence that is still the single source of
truth, and wrong colors and shapes counting as one wrong step with no
special case**, accepting that **the counter only tells 0, 1, and "two or
more" apart, not 2 from 5; it tries every place a step could have moved to,
which is fine for sequences of at most about 16 steps; and a few unusual
sequences can land on a different count than a person might expect (for
example swapping two steps that are far apart, such as File and Polish, is
"two or more", because two steps moved, while a side-by-side swap is
one).**

## Why the alternatives were not chosen

- **Plain edit distance (Levenshtein).** Moving one step counts as two
  changes (take it out, put it back somewhere else), so Polish before Buff
  would earn $0. The student's answer said a step in the wrong place is one
  mistake.
- **Edit distance with swaps (Damerau).** This fixes side-by-side swaps
  but still counts a step moved further, such as the health question asked
  last, as two or more.
- **Separate rule checks.** Each rule would need its own code, and one slip
  can break several rules at once: a missing Buff also breaks "Pick polish
  color comes right after Buff". The count would then be too high, and every
  new step would need new rules. Decision 0001 rejected this for the same
  reasons.

## Examples

| Player's steps compared to the correct ones           | Count |
|--------------------------------------------------------|-------|
| exactly right                                          | 0     |
| Buff left out                                          | 1     |
| a second "Ask client to wash hands"                    | 1     |
| Grape picked instead of Cherry Red                     | 1     |
| Polish before Buff (a swap)                            | 1     |
| health question asked last instead of first            | 1     |
| Buff left out and the health question left out         | 2     |
| a wrong color and a missing Buff                       | 2     |
| one mistake on the hands and one on the feet (combo)   | 2     |

## Tests that had to change

Five earlier tests expected a single mistake to earn $0. Each still checks
the requirement it names:

- `tests/test_r5_star.py`: the wrong-order test now swaps two pairs of steps,
  so it is still a $0 case.
- `tests/test_r11_diabetes.py`, `tests/test_r12_polish_color.py`,
  `tests/test_r13_nail_shape.py`: nipping a diabetic client, a wrong color,
  and a wrong shape are still mistakes (not satisfied), but alone they now
  earn half. The tests were renamed to say so.
- `tests/test_r7_browser.py`: the finish reply now includes `mistakes`.

The new behavior is checked in `tests/test_r5_half_star.py`.
