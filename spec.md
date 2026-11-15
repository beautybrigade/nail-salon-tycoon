# Nail Salon Tycoon — Spec (round 1)

A terminal game in which the player is a first-time nail technician working one
day in a salon. This spec describes how the game meets each requirement in
`problem.md` (R1–R6). Decisions marked **(student)** were answered by the
student before round 1; the rest were chosen by the assistant and may be
revisited.

## Services **(student)**

| Service           | Price | Areas worked on        | Hand service? |
|-------------------|-------|------------------------|---------------|
| Manicure          | $25   | hands                  | yes           |
| Pedicure          | $35   | feet                   | no            |
| Mani + Pedi combo | $55   | hands, then feet       | yes           |

For the combo, the hands are always done first, then the feet.

## The work day (R1, R6) **(student)**

- The salon is open from 9:00 to 17:00. Every client takes up a one-hour slot,
  and the last slot starts at 16:00.
- There are **6 clients** in a day:
  - **3 appointments** at fixed times: **10:00, 12:00, 14:00**.
  - **3 walk-ins** who show up at random. Each walk-in gets a different hour,
    picked at random from the free hours (9, 11, 13, 15, 16), so a walk-in
    never collides with an appointment.
- Clients are served in time order. The game says whether each client is an
  appointment or a walk-in.
- Each client's service is chosen at random (all three equally likely), and so
  is whether they already have product on their nails (50% chance) and whether
  they have a health condition (see R2).
- All randomness comes from a `random.Random` object that is passed in, so a
  seed gives the same day every time (this is how the tests are repeatable).

## Steps the player can take (R2, R3, R4) **(student: one step at a time)**

For each client, the player picks steps one at a time from a numbered menu:

1. Ask about health conditions
2. Ask client to wash hands
3. Remove product
4. File
5. Buff
6. Polish
7. Finish service

The player can pick any step in any order. The game does not stop them; it
judges the whole sequence when they choose **Finish service**.

### The correct sequence

For each client the one correct sequence is:

1. **Ask about health conditions** (R2), once, first, for every service.
2. Then, for each area in service order (hands, then feet for a combo):
   - **Ask client to wash hands** (R3), only before working on the hands.
     Never for a pedicure, and for a combo only once, before the hands.
   - **Remove product** (R4), only if the client arrived with product on.
   - **File**, then **Buff**, then **Polish** (R4).

Examples:

- Manicure, no product: health, wash, file, buff, polish
- Pedicure, with product: health, remove, file, buff, polish
- Combo, with product: health, wash, remove, file, buff, polish, remove, file,
  buff, polish

(For a combo, "has product" applies to both hands and feet.)

### Health conditions (R2)

When the player asks, the client answers either "No conditions" or one of a
small fixed list (for example "sensitive skin", "diabetes", "allergic to
acetone"). In round 1 the answer is shown to the player for information only;
it does not change the correct sequence.

## Mistakes **(student: any skipped or wrong step)**

The client is **unsatisfied** if the player's sequence is not exactly the
correct sequence. That includes:

- not asking about health conditions, or asking later than first;
- not asking for hand washing before a hand service;
- asking for hand washing when it isn't needed (a pedicure, or the feet part of
  a combo);
- skipping product removal when product is on, or removing product when there
  is none;
- skipping filing, buffing, or polishing, or doing them out of order;
- repeating a step that should only happen once.

## Star and earnings (R5)

- When the service is finished, the client gives the player **1 star if
  satisfied** and **0 stars if unsatisfied**.
- A star means the player earns the **full price** of the service. No star
  means **$0** for that client. There are no tips and no partial payment.

## End of the day (R6) **(student: goal $150)**

After the 6th client the game shows:

- each client's time, type (appointment or walk-in), service, star, and amount
  earned;
- the **total earnings** for the day;
- whether the **daily goal of $150** was met (total ≥ $150 counts as met).

## Running

- One command starts the game: `python3 game.py`. Add `--seed N` to replay the
  same day.
- Tests: `python3 -m pytest`.
- Only the Python standard library is used. pytest is the only extra tool.
