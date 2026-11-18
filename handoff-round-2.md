# Handoff: end of round 2

For a fresh session starting round 3. Read `CLAUDE.md` (standing rules),
`problem.md` (requirements), `spec.md` (how they are met), and
`docs/decisions/` first. This file covers only what those don't.

There was no handoff file from round 1; round 2 worked from the files above.

## Current state

- Requirements R1–R6 (round 1, terminal game) and R7–R8 (round 2, browser
  game with animation) are implemented.
- `python3 -m pytest`: **84 passed** in about 1 second (46 from round 1, 38
  new). The working tree was clean at the end of round 2.
- Round 2 commits, oldest first:
  - `c692993` spec: round 2 sections, with the student's answers
  - `7754be8` failing tests for R7 and R8 (written before the code)
  - `edac3a2` salon.py: polish colors, nail looks, `Game` class
  - `ab904ba` web.py: local server that opens the browser
  - `c8df7a6` static/: the animated page
  - `6bdcb19` decision records 0002 and 0003
  - `bcbfbe8` README: how to start the browser game

### Files

| File | What it holds |
|------|---------------|
| `salon.py` | All rules. Round 2 added `POLISH_COLORS`, `Client.polish_color`, `NailLook`, `working_area`, `nail_looks`, and `Game` (a day in progress). |
| `game.py` | Terminal front end (unchanged in round 2; does not use `Game`). |
| `web.py` | Local server: serves `static/`, answers `POST /api/new-game`, `/api/step`, `/api/finish` in JSON, keeps one `salon.Game` per game id. Also `STEP_ANIMATIONS` (step → animation name). |
| `static/index.html` | Page layout and the SVG scene (table, hand view, foot view, tools). |
| `static/style.css` | Colors, layout, nail-state classes, and one `@keyframes` per step. |
| `static/app.js` | Draws fingers/toes, calls the server, plays animations, shows results. No rules. |
| `tests/test_r7_browser.py` | `Game`, the server's pages and JSON interface, the one command. |
| `tests/test_r8_animation.py` | Animation names exist in web.py / app.js / style.css, nail looks, colors. |

## How to run

From this folder:

```bash
cd nail-salon-tycoon
python3 web.py              # browser game; opens the default browser
python3 web.py --seed 42    # same day every time; also --port N, --no-browser
python3 game.py             # terminal game (also takes --seed)
python3 -m pytest           # all tests
```

`web.py` keeps running until Ctrl+C. Python 3.10+ (developed on 3.13.7).

## Decisions made in round 2 and why

**Answered by the student** (marked **(student)** in spec.md):

- One command opens the browser itself (not just printing a link).
- Wrong steps still animate; mistakes are judged only at Finish, as in round 1.
- Each client requests a polish color; color is not judged.
- Keep the terminal game alongside the browser game.

**Made by the assistant; the student accepted these in round 2:**

1. Rules stay in Python; the page asks the server for every step (decision
   0002), so there is one copy of the rules and pytest covers them.
2. Standard-library `http.server`, not Flask and not a file-only page.
3. Server listens on `127.0.0.1` only; default port 8000, falls back to any
   free port if busy.
4. Extra options `--seed`, `--port`, `--no-browser` (`--no-browser` also makes
   tests possible).
5. A combo switches from hands to feet after the first Polish, however the
   earlier steps went (decision 0003).
6. Nail look replays exactly what the player did, so wrong orders still show
   (decision 0003), and no hint about mistakes appears before Finish.
7. The 8-color palette and its names.
8. The color is drawn from the same seeded `random.Random`, so seeds give
   different days than in round 1.
9. Drawing: client's right hand on a striped towel (thumb on screen right);
   foot on a purple footrest.
10. The look of each animation and each nail state (see spec.md tables).
11. Extras: confetti, "Hands done! Now the feet." banner, star counter,
    "Play another day" button.
12. Short animations for reduced-motion settings; step buttons locked during
    an animation.
13. A failed service shows the correct steps (same as the terminal game).
14. `salon.Game` class, so the server can track where each player is.
15. Test server polls for shutdown every 0.05 s (tests went from 8 s to 1 s).
16. Two decision records instead of the minimum one; README updated.

## Unresolved

- Played end to end by the student in a real browser in round 2; it works.
- A white band at the top during animations was seen only in headless screenshots; not seen in a real browser.
- `game.py` still runs its own loop instead of using `salon.Game`. That's fine,
  but it's two ways of walking through a day.
- The server never forgets finished games (`SalonServer.games` only grows).
  Harmless for one player on one computer; worth knowing.

## Warnings for the next session

- **This folder is its own git repository**, nested inside the course repo
  (`csc299-main`), where `Final Project/` shows as untracked. Run git commands
  from this folder, and commit here, not in the outer repo.
- **JavaScript is not tested by pytest.** Tests only check that each step's
  animation name appears in `app.js` and as `@keyframes` in `style.css`.
  Node is not installed. To see the page, run the server and use headless
  Chrome, for example:
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --window-size=1280,860 --virtual-time-budget=3000 --screenshot=out.png http://127.0.0.1:8000/`
  (start it with `--no-browser`, and stop the server afterwards).
- **Animation names must match in three places:** `web.py` `STEP_ANIMATIONS`,
  the `ANIMATIONS` object in `static/app.js`, and `@keyframes` in
  `static/style.css`. **Durations are written twice:** `ms` in app.js and the
  `animation:` length in style.css; change both together.
- Tools animate along a fixed line near y ≈ 290–312 in the SVG (viewBox
  600×440) that works for both the hand and the foot. Moving fingers or toes
  means checking the tool keyframes too.
- `Client` gained a sixth field, `polish_color`, with a default. The test
  helper `tests/helpers.py` `make_client(..., color=...)` sets it.
- Adding a random draw to `_random_client` or `generate_day` changes every
  seeded day. No test depends on exact seeded values, but players replaying a
  seed will see a different day.
- If port 8000 is busy (for example a server left running), `web.py` picks
  another port; check the printed link.
