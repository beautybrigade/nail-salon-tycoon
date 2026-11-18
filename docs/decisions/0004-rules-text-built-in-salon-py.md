# 0004: Build the rules text in salon.py from the game's own settings

Status: accepted (round 3)

In the context of **showing the rules before the day begins (R9) in both the
terminal game and the browser game**, facing **rules that repeat facts the
game already holds (prices, appointment times, the daily goal, the step
names and their order), the standing rule that no game rule may be written in
JavaScript, and a step list that changed in this same round (R3 added
"Wash feet in foot bath")**, we decided for **one function, `salon.rules()`,
that builds the rules as headings and lines from the same constants and
`Step` labels the game uses; `game.py` prints them and the page fetches them
from `GET /api/rules`**, and neglected **writing the rules by hand in
`index.html` (and again in `game.py`), keeping them in a separate text or
Markdown file that both read, and listing the exact correct steps by calling
`required_steps()` for a sample client of each service**, to achieve **a
single copy of the rules that cannot drift from the real game (changing the
goal or a price changes the rules too, and a test checks this), the same words
in both versions, and tests that can check what the rules say**, accepting
that **the wording now lives in Python code instead of a page a designer could
edit, rule lines are plain text with no bold or links, and the page needs one
more request to the server before it can show anything.**
