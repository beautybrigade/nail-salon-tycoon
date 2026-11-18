# 0002: Keep the rules in Python and serve the browser page from a local server

Status: accepted (round 2)

In the context of **making the game playable in a browser, started with one
command (R7)**, facing **the fact that a browser runs JavaScript, not Python,
while every rule of the game (and all 46 round 1 tests) lives in `salon.py`**,
we decided for **a small standard-library web server (`web.py`, using
`http.server`) that serves the page in `static/` and answers the page over a
JSON interface (`/api/new-game`, `/api/step`, `/api/finish`), so the page only
draws and animates while `salon.py` decides every step, star, and total**, and
neglected **rewriting the rules in JavaScript as a single page you open
straight from a file (no server), keeping two copies of the rules (Python for
the terminal, JavaScript for the browser), and a third-party Python web
framework such as Flask**, to achieve **one copy of the rules that both the
terminal game and the browser game use, rules and nail looks that stay tested
with pytest, and a project that still needs only the standard library**,
accepting that **the game needs a running Python process (closing the terminal
closes the salon), each step makes a request to the server, and the page's
drawing and animation code is not covered by the Python tests (they only
check that each step's animation exists in the page files).**
