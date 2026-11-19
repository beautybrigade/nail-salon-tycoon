# 0006: Nipping a diabetic client's cuticles is a judged mistake (R11)

Status: accepted (round 4)

In the context of **R11, where the student asked that "if the client responds
with a diabetic medical condition, nipping cuticles must be excluded from the
service requirements", on top of R10's new Nip cuticles step between File and
Buff**, facing **a judging rule that compares the player's steps to one exact
sequence (decision 0001), a requirement that says what is excluded but not
what happens if the player nips anyway, a health answer that the player only
learns by asking, and the real-world reason behind R11 (a small cut heals
slowly and can get infected in a person with diabetes)**, we decided for
**leaving `Step.NIP_CUTICLES` out of `required_steps()` for every area of a
client whose `health_condition` is diabetes, so that nipping such a client
anyway counts as an extra step and makes them unsatisfied (no star, $0); the
exception follows the client's real condition, not whether the player asked,
and the rules screen says "Never nip the cuticles of a client with
diabetes"**, and neglected **making nipping optional for diabetic clients
(allowed or skipped, either way a star); following only what the player has
heard, so a player who never asked would still be expected to nip; and
playing a warning or blocking the Nip cuticles button once the client says
"diabetes"**, to achieve **a game that teaches the real lesson (listen to the
health answer, and don't cut a diabetic client's skin), finally gives the R2
health question a consequence, and needs no new kind of judging, just one
more condition in `required_steps()`**, accepting that **a player can lose a
star on a client they never asked about (though skipping the question already
costs the star under R2), diabetic clients come up rarely (about 1 client in
10, since 30% of clients have a condition and diabetes is 1 of 3), so a player
may play a whole day without seeing the exception, and a correct service for a
diabetic client ends with the cuticles still drawn ragged in the browser.**

## Why the alternatives were not chosen

- **Optional for diabetic clients.** R11 says "excluded", which reads more
  like "left out" than "up to you". An optional step would be the only one in
  the game. `finish_service` would need a second way of comparing sequences,
  and the player would learn nothing from the health answer. The student
  chose "it's a mistake" when asked.
- **Follow only what the player heard.** This would make the expected steps
  depend on whether the player asked first. `required_steps()` would need the
  player's own steps as input, and the "correct steps were" list would change
  depending on what the player did. That isn't needed: R2 already makes "not
  asking first" a mistake, so a player who skips the question gets no star
  either way.
- **Warn or block in the interface.** The game's style since round 2 is "show
  what you did, judge at the end" (decision 0003). Blocking the button would
  give away the answer and would also need logic in JavaScript or `game.py`,
  which the standing rules forbid.

## Tests that had to change

R10 added a step to every non-diabetic service, so six earlier tests that
spell out an exact sequence or a finished nail look now include
`NIP_CUTICLES`. Each one still checks the requirement it names:

- `tests/test_r4_steps.py`: the manicure, pedicure, and combo exact
  sequences (3 tests).
- `tests/test_r3_foot_washing.py`: the pedicure sequence and the combo's
  feet half (2 tests).
- `tests/test_r8_animation.py`: the fully finished manicure look now has
  `cuticles_nipped=True` (1 test).

`NailLook.cuticles_nipped` defaults to `False`, so the other tests that build
a `NailLook` did not need to change. The new behavior is checked in
`tests/test_r10_cuticles.py` and `tests/test_r11_diabetes.py`.
