# Nail Salon Tycoon — Spec (rounds 1 to 6)

A game in which the player is a first-time nail technician working one day in a
salon. Round 1 made it a terminal game (R1–R6). Round 2 adds an animated
browser version (R7, R8); the rules of the day stay the same. Round 3 adds a
rules screen before the day begins (R9) and a foot-washing step for pedicures
(R3 changed). Round 4 adds a cuticle-nipping step (R10) that is skipped for
clients with diabetes (R11). Round 5 makes the player pick the client's polish
color off a polish wall (R12) and file the hands into the client's chosen nail
shape (R13). Round 6 changes R5: a service with exactly one mistake earns
half a star and half the price. Decisions marked
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

(Round 3 added step 3, **Wash feet in foot bath**; round 4 added step 6,
**Nip cuticles**; round 5 added step 8, **Pick polish color**, and a shape
choice when filing the hands; see "Round 3", "Round 4", and "Round 5" below.)

For each client, the player picks steps one at a time from a numbered menu:

1. Ask about health conditions
2. Ask client to wash hands
3. Wash feet in foot bath
4. Remove product
5. File
6. Nip cuticles
7. Buff
8. Pick polish color (round 5: the player then picks one color from the wall)
9. Polish
10. Finish service

(Round 5) **File** on the hands also asks the player which shape to file:
square, round, stiletto, or almond. File on the feet asks nothing.

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
   - **File**, then **Nip cuticles** (R10, round 4), then **Buff**, then
     **Polish** (R4). **Nip cuticles** is left out when the client has
     diabetes (R11, round 4).
   - (Round 5) On the hands, **File** must use the client's chosen shape
     (R13). On the feet, File has no shape.
   - (Round 5) **Pick polish color**, with the client's color, comes right
     after Buff and right before Polish (R12). In a combo it is picked only
     once, before the hands' Polish; the feet reuse the same bottle.

Examples (round 5; "file (almond)" means File with the almond shape, and
"pick (Grape)" means Pick polish color with Grape):

- Manicure, no product, almond, Grape: health, wash hands, file (almond),
  nip, buff, pick (Grape), polish
- Pedicure, with product, Grape: health, wash feet, remove, file, nip, buff,
  pick (Grape), polish
- Combo, with product, square, Grape: health, wash hands, remove,
  file (square), nip, buff, pick (Grape), polish, wash feet, remove, file,
  nip, buff, polish
- Manicure, client has diabetes, round, Grape: health, wash hands,
  file (round), buff, pick (Grape), polish

(For a combo, "has product" and "has diabetes" apply to both hands and feet.)

### Health conditions (R2)

When the player asks, the client answers either "No conditions" or one of a
small fixed list ("sensitive skin", "diabetes", "allergic to acetone"). From
round 4, **diabetes** changes the correct sequence (R11, see "Round 4" below).
The other answers are still shown for information only.

## Mistakes **(student: any skipped or wrong step)**

The client is **unsatisfied** if the player's sequence is not exactly the
correct sequence. From round 6, the game also counts **how many** mistakes
there were (see "Round 6" below). Mistakes include:

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
- skipping cuticle nipping for a client without diabetes, or nipping anywhere
  other than right after filing and right before buffing (round 4);
- nipping the cuticles of a client with diabetes (round 4);
- not picking the polish color, picking it anywhere other than right after
  Buff and right before Polish, picking the wrong color, or picking it a
  second time in a combo (round 5, R12);
- filing the hands in a shape other than the client's (round 5, R13);
- repeating a step that should only happen once.

## Star and earnings (R5, changed in round 6)

When the service is finished, the game counts the player's mistakes (see
"Round 6: half a star for one mistake" below):

| Mistakes     | Stars | Pay             | Manicure | Pedicure | Combo  |
|--------------|-------|-----------------|----------|----------|--------|
| none         | 1     | full price      | $25      | $35      | $55    |
| exactly one  | ½     | half the price  | $12.50   | $17.50   | $27.50 |
| two or more  | 0     | $0              | $0       | $0       | $0     |

There are no tips. Only a service with no mistakes counts as "satisfied".

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
| Nip cuticles                | (round 4) see "Round 4: cuticle nipping" below      |
| Buff                        | a buffer block rubs in circles over the nails       |
| Polish                      | a brush sweeps color onto the nails, then sparkles  |

The player can't pick another step while an animation is playing.

### The nails change as the player works **(student)**

Each area (hands, feet) has a nail look that the server works out from the
steps taken so far:

- **old product**: if the client arrived with product, the nails show a dull,
  chipped old color until **Remove product**;
- **filed**: after **File**, the nails have a short, smooth, rounded tip;
- **cuticles nipped** (round 4): every nail starts with a ragged cuticle edge
  at its base; after **Nip cuticles** the edge is a clean, neat line;
- **buffed**: after **Buff**, the nails have a soft shine;
- **polished**: after **Polish**, the nails are the color the player picked
  off the wall (round 5, R12) with a glossy shine;
- **shape** (round 5, R13): after **File** on the hands, the nails have the
  shape the player chose.

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
- Until round 4, the requested color was what the Polish step painted and
  color was not judged. From round 5, the player picks the color and it is
  judged (R12, see "Round 5" below).
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
    remove product only if there is old polish, then file, nip cuticles
    (round 4: never for a client with diabetes), buff, polish;
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

## Round 4: cuticle nipping (R10, R11)

- **Nip cuticles** is a new step the player must pick, judged like every other
  step (see "The correct sequence" and "Mistakes" above). It comes right after
  **File** and right before **Buff** (R10).
- In a combo, the cuticles are nipped on **both** the hands and the feet, once
  per area. **(student)**
- **Diabetes (R11):** if the client's health condition is diabetes, the
  correct sequence has no **Nip cuticles** at all (for a combo, on neither
  area). Nipping a diabetic client's cuticles anyway is a **mistake**: no star,
  $0, like any extra step. **(student)**
- The exception follows the client's real condition, whether or not the
  player asked. A player who doesn't ask about health conditions already gets
  no star (R2), so this never rewards skipping the question.
- The rules screen (R9) says where nipping goes and that it is never done for
  a client with diabetes. As before, the text is built in `salon.rules()`.
- Both versions get the new step. In the terminal it prints "You carefully
  nip the cuticles."
- Animation (browser): a pair of bright cuticle nippers moves across the base
  of the nails, its jaws snipping open and shut. The animation name is
  `nip-cuticles`, 1.8 s long. Halfway through, the nails change to the
  "cuticles nipped" look. **(student: the nails change)**
- The ragged cuticles are shown for every client at the start, including
  clients with diabetes, so the picture never gives away the health answer.
  For a diabetic client, a correct service ends with the cuticles still
  ragged.
- Like every wrong step, nipping at the wrong time still plays the animation
  and changes the nails, and is judged only at **Finish**.
- Adding the step adds no new random draw, so a given `--seed` gives the same
  clients as in round 3.

## Round 5: picking the polish color (R12)

- When a client arrives, the game shows the color they want (the terminal now
  prints it too). The color is the client's existing random color from
  round 2, so this adds no new random draw.
- **Pick polish color** is a new step, judged like every other step. It must
  come right after **Buff** and right before **Polish** (R12). The player
  chooses a color from the polish wall: all 8 colors in `POLISH_COLORS`.
  **(student: a new step)**
- A wrong color is a mistake: no star, $0. Missing the pick, picking at the
  wrong time, or picking twice is also a mistake.
- **Combo:** the color is picked **once**, before the hands' Polish. The feet
  are polished with the same bottle, so picking again before the feet's
  Polish is an extra step. **(student)**
- **Polish paints the picked color** (the most recent pick), even when it is
  the wrong one. **(student: show what the player picked)** If the player
  polishes without having picked a color, the brush uses the client's
  requested color (judged as a mistake at Finish anyway).
- Terminal: after choosing the step, the player types the number of a color
  from a numbered list, and the game prints "You take the <color> bottle off
  the polish wall."
- Browser: the step opens a polish wall of 8 colored bottles to click. Its
  animation, `pick-color` (1.2 s), lifts a bottle of the picked color off
  a shelf and sets it on the table. It does not change the nails.

## Round 5: filing the nail shape (R13)

- Every manicure and combo client chooses a nail shape when they arrive,
  picked at random from **square, round, stiletto, almond**. Pedicure clients
  have no shape. The shape is shown with the service when the client arrives.
- **File asks for the shape on the hands.** **(student: the File step asks)**
  When the player picks File while working on the hands, the game asks which
  shape. The shape must match the client's: a wrong shape is a mistake (no
  star, $0). There is no separate "shape" step, so "shaping right before
  filing" is part of the File step itself.
- File on the feet (a pedicure, or the feet of a combo) asks nothing,
  exactly as before.
- **The nails show the shape the player filed** (right or wrong).
  **(student)** Before filing, the nails keep their natural look. After a
  plain File on the feet, the toenails get the short, smooth tip from round 2.
- Terminal: after choosing File on the hands, the player types the number of
  a shape, and the game prints "You file the nails into a <shape> shape."
- Browser: File on the hands first opens a shape picker with the 4 shapes.
  The file animation (unchanged) plays, and halfway through the nails take
  on the chosen shape.
- The server decides when File needs a shape and when Pick polish color
  needs a color (`salon.choices_for()`); the page and `game.py` only ask the
  question they are told to ask.

## Round 5 notes

- The shape is a new random draw, made after the color and only for clients
  with a hand service. So a given `--seed` gives different days than in
  round 4.
- The rules screen (R9) adds the color pick and the shape. As before, the
  text is built in `salon.rules()`.
- Menu numbers: Pick polish color is step 8, so Polish is 9 and Finish is 10.

## Round 6: half a star for one mistake (R5 changed)

### What counts as one mistake **(student: any one mistake)**

The game compares the player's steps to the one correct sequence (decision
0001) and counts the mistakes as **0**, **1**, or **2 or more**. It is
exactly **one** mistake when one of these changes turns the player's steps
into the correct sequence:

- **one skipped step**: one correct step is missing (for example no Buff, or
  no health question);
- **one extra step**: one step too many (for example a second hand wash, a
  Remove product when there was no old polish, or picking the color again
  for the feet of a combo);
- **one wrong step**: one step in the right place is the wrong one. A wrong
  polish color or a wrong nail shape is one wrong step (R12, R13);
- **one step in the wrong place**: one step taken out and done somewhere
  else, near or far (for example Polish before Buff, or the health question
  asked last). This counts as one mistake, not two.

Anything else, such as two skipped steps, a skipped step plus a wrong color,
or two steps moved, is two or more mistakes: no star and $0. The rule is
written once, in `salon.py` (`count_mistakes()`), see decision 0008.

- **Safety mistakes count the same** **(student)**: not asking about health
  conditions, or nipping a diabetic client's cuticles, is one mistake like
  any other. If it is the only one, the player still gets half a star and
  half pay.
- **A combo is one service** **(student)**: mistakes are counted across the
  hands and the feet together. One mistake anywhere earns $27.50; one on the
  hands and one on the feet earns $0.

### Money with cents **(student: keep the cents)**

- Half pay is exactly half the price: $12.50, $17.50, $27.50. The day's total
  can have cents (for example $142.50), and the $150 goal is checked against
  that exact total.
- Amounts are kept as exact decimals (Python's `Decimal`), never as rounded
  floats, see decision 0009. Prices stay whole dollars.
- Amounts are shown with cents only when there are cents: "$25", "$12.50",
  "$142.50". `salon.money()` makes this text for the terminal and the rules;
  the page writes amounts the same way.

### What the player sees

- After a service with one mistake, the terminal prints
  "The client is partly satisfied: one step was wrong. Half a star! +$12.50"
  and then the correct steps, as it does after a failed service.
- The browser result pop-up shows a half star, the same message, the amount,
  and the correct steps.
- Stars are shown as ★ for one, ½ for half, and – for none, in the end-of-day
  summary (terminal and browser). The browser's star counter adds up the
  day's stars, sent by the server.
- The rules screen (R9) explains full, half, and no pay. As before, the text
  is built in `salon.rules()`.
- Confetti only for a full star.

### Notes

- `ServiceResult` gains `mistakes` (0, 1, or 2 meaning "2 or more").
  `stars` and `earned` are `Decimal`s; `satisfied` stays true only with no
  mistakes.
- The JSON from `web.py` sends `stars`, `earned`, and totals as numbers
  (for example `0.5` and `12.5`), plus `mistakes`.
- Round 6 adds no random draw, so a given `--seed` gives the same day as in
  round 5.

## Running

- Browser game: `python3 web.py` (R7). Terminal game: `python3 game.py`. Both
  take `--seed N` to replay the same day.
- Tests: `python3 -m pytest`.
- Only the Python standard library is used. pytest is the only extra tool.
