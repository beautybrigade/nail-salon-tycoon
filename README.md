# Nail Salon Tycoon

A game for trying out a day in a nail salon before you work in one. Play it
in your browser, with animations from the nail technician's seat, or in the
terminal.
You play a first-time nail technician with 6 clients: 3 appointments at set
times and 3 walk-ins who show up at random. For each client you pick the steps
of the service one at a time:

- ask about health conditions,
- ask the client to wash their hands (before working on hands),
- wash their feet in the foot bath (before working on feet),
- remove old product if there is any,
- file, nip the cuticles, buff, and polish (never nip the cuticles of a
  client with diabetes).

Do every step in the right order and the client gives you a star and pays for
the service (Manicure $25, Pedicure $35, Mani + Pedi combo $55). Get anything
wrong and you earn nothing for that client. At the end of the day you see your
total earnings and whether you met the $150 daily goal.

The game shows these rules before the day begins. The full rules are in
[spec.md](spec.md).

## Run the game

In the browser (opens automatically):

```bash
python3 web.py
```

Press Ctrl+C in the terminal to close the salon. Options: `--seed 42` replays
the same day, `--port 8001` picks another port, `--no-browser` only prints the
link.

In the terminal:

```bash
python3 game.py
```

To replay the same day, give it a seed: `python3 game.py --seed 42`.

## Run the tests

```bash
python3 -m pytest
```

You need Python 3.10 or newer. The game uses only the standard library, and
pytest is the only extra tool.

## Files

- `salon.py`: all the game rules (no input or printing)
- `game.py`: the terminal menus and messages
- `web.py`: the local web server for the browser version
- `static/`: the browser page (HTML, CSS animations, JavaScript)
- `tests/`: one test file per requirement (R1–R11; R3 has two, for hand and
  foot washing)
- `docs/decisions/`: decision records
