# Nail Salon Tycoon — Spec (rounds 1 to 3)

A game in which the player is a first-time nail technician working one day in a
salon. Round 1 made it a terminal game (R1–R6). Round 2 adds an animated
browser version (R7, R8); the rules of the day stay the same. Round 3 adds a
rules screen before the day begins (R9) and a foot-washing step for pedicures
(R3 changed). Decisions marked
**(student)** were answered by the student; the rest were chosen by the
assistant and may be revisited.

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
- Clients are served in time order. When a client arrives, the game shows
  their time, whether they are an appointment or a walk-in, their service and
  price, and whether they already have product (old polish) on their nails.
- Each client's service is chosen at random (all three equally likely), and so
  is whether they already have product on their nails (50% chance) and whether
  they have a health condition (see R2).
- All randomness comes from a `random.Random` object that is passed in, so a
  seed gives the same day every time (this is how the tests are repeatable).

## Steps the player can take (R2, R3, R4) **(student: one step at a time)**

(Round 3 added step 3, **Wash feet in foot bath**; see "Round 3" below.)

For each client, the player picks steps one at a time from a numbered menu:

1. Ask about health conditions
2. Ask client to wash hands
3. Wash feet in foot bath
4. Remove product
5. File
6. Buff
7. Polish
8. Finish service

The player can pick any step in any order. The game does not stop them; it
judges the whole sequence when they choose **Finish service**.

### The correct sequence

For each client the one correct sequence is:

1. **Ask about health conditions** (R2), once, first, for every service.
2. Then, for each area in service order (hands, then feet for a combo):
   - **Ask client to wash hands** (R3), only before working on the hands.
     Never for a pedicure, and for a combo only once, before the hands.
   - **Wash feet in foot bath** (R3, round 3), only before working on the
     feet. Never for a manicure, and for a combo only once, after the hands
     are polished and before any work on the feet.
   - **Remove product** (R4), only if the client arrived with product on.
   - **File**, then **Buff**, then **Polish** (R4).

Examples:

- Manicure, no product: health, wash hands, file, buff, polish
- Pedicure, with product: health, wash feet, remove, file, buff, polish
- Combo, with product: health, wash hands, remove, file, buff, polish,
  wash feet, remove, file, buff, polish

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
- not washing the feet before working on them (round 3);
- washing the feet when it isn't needed (a manicure, or before the hands are
  done in a combo) (round 3);
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

## Round 2: playing in the browser (R7) **(student)**

- One command starts the browser game: `python3 web.py`. It starts a small web
  server on the player's own computer (address `http://127.0.0.1:<port>/`,
  reachable only from this computer) and opens the game in the default browser.
  Add `--seed N` to replay the same day, `--port N` to choose the port (default
  8000), and `--no-browser` to skip opening the browser.
- The terminal game still works: `python3 game.py`. Both versions use the same
  rules in `salon.py`.
- The browser plays the same day as the terminal game: 6 clients in time
  order, the same 6 steps plus **Finish service**, the same judging (R5), and
  the same end-of-day summary (R6).
- Game rules stay in Python (`salon.py`). The page asks the server for each
  result over a small JSON interface (see decision 0002), so the browser never
  decides whether a client is satisfied.
- Everything needed is in this repository: no internet, no downloaded
  libraries, standard library only.

## Round 2: animation (R8)

### Point of view **(student: the nail technician's)**

The player looks down at the work table from the technician's seat: the
client's hand (or foot) rests on the table with the fingertips (or toes)
pointing toward the player, so the nails are in full view. The technician's
tools come in from the player's side of the table.

For a combo, the hands are shown first. The view switches to the feet after the
first **Polish** step (the hands are done), matching "hands, then feet".

### Each step has its own animation **(student)**

| Step                        | Animation                                           |
|-----------------------------|-----------------------------------------------------|
| Ask about health conditions | the client answers in a speech bubble               |
| Ask client to wash hands    | soap bubbles rise around the hand                   |
| Wash feet in foot bath      | (round 3) see "Round 3: foot washing" below         |
| Remove product              | a cotton pad wipes across the nails                 |
| File                        | a nail file slides back and forth over the nails    |
| Buff                        | a buffer block rubs in circles over the nails       |
| Polish                      | a brush sweeps color onto the nails, then sparkles  |

The player can't pick another step while an animation is playing.

### The nails change as the player works **(student)**

Each area (hands, feet) has a nail look that the server works out from the
steps taken so far:

- **old product**: if the client arrived with product, the nails show a dull,
  chipped old color until **Remove product**;
- **filed**: after **File**, the nails have a short, smooth, rounded tip;
- **buffed**: after **Buff**, the nails have a soft shine;
- **polished**: after **Polish**, the nails are the client's requested color
  with a glossy shine.

Steps change the area being worked on (hands, then feet after the first
Polish in a combo). Wrong steps still animate and change the nails; for
example, polishing before filing still paints the nails.
**(student: show what you did, judge at the end)** Mistakes are only judged at
**Finish service**, the same as round 1.

### Lots of color **(student: client requests a color)**

- Each client asks for a polish color when they arrive, picked at random from a
  fixed palette of bright colors (for example Cherry Red, Hot Pink, Sunny
  Yellow, Electric Blue). The color comes from the same seeded `random.Random`,
  so a seed gives the same colors.
- The requested color is what the Polish step paints. Color choice is not
  judged.
- The salon itself is colorful: bright background, colored tools and bottles,
  confetti when the client gives a star.

## Round 3: rules screen (R9) **(student: show the full step order)**

- Before the day starts, the game shows the rules. The day begins only when
  the player chooses to begin.
  - Browser: the rules appear in a window over the salon with a
    **Begin the day** button. No client is created until the player presses it.
  - Terminal: `game.py` prints the rules, then waits for the player to press
    Enter before the first client arrives.
- The rules say:
  - how the day works: opening hours, 6 clients, the 3 appointment times, and
    that 3 walk-ins come at random times;
  - the services and their prices (the combo is hands first, then feet);
  - the full correct order of steps: health question first; then for each area
    wash it (hands: ask client to wash hands; feet: wash feet in foot bath),
    remove product only if there is old polish, then file, buff, polish;
  - that the client gives a star and pays the full price only if every step is
    right, and pays nothing otherwise;
  - the daily goal ($150).
- The rules text is written once, in `salon.py`, built from the same settings
  the game uses (prices, goal, hours), so it can't go out of date. Both the
  terminal and the browser show that text (see decision 0004).
- "Play another day" in the browser goes straight to a new day without showing
  the rules again.

## Round 3: foot washing for pedicures (R3 changed) **(student)**

- Washing the feet is a new step the player must pick, **Wash feet in foot
  bath**, judged like every other step (see "The correct sequence" and
  "Mistakes" above). It works for the feet the way hand washing works for the
  hands. **(student: required step, judged)**
- In a combo, the feet are washed after the hands are polished, just before
  the work on the feet starts. **(student)**
- Both versions get the new step. **(student)** In the terminal it prints
  "The client's feet soak in the warm foot bath."
- Animation (browser): a foot bath of blue water rises around the foot, with
  ripples and bubbles, then drains away. Like hand washing, it does not change
  the nails. The animation name is `wash-feet`, separate from `wash-hands`.
- Like every wrong step, picking it at the wrong time still plays the
  animation, on whichever area is shown, and is judged only at **Finish**.

## Running

- Browser game: `python3 web.py` (R7). Terminal game: `python3 game.py`. Both
  take `--seed N` to replay the same day.
- Tests: `python3 -m pytest`.
- Only the Python standard library is used. pytest is the only extra tool.
