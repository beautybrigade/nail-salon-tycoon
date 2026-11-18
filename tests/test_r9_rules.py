"""R9: the game shows the rules at the beginning, before the player chooses
to begin the day."""

import json
import re
import threading
import urllib.request
from pathlib import Path

import pytest

import game
import salon

STATIC = Path(__file__).resolve().parent.parent / "static"


def rules_text():
    return "\n".join([s.heading for s in salon.rules()]
                     + [line for s in salon.rules() for line in s.lines])


# --- What the rules say (written once, in salon.py) ----------------------------

def test_r9_rules_explain_the_day():
    text = rules_text()
    assert f"{len(salon.APPOINTMENT_HOURS) + salon.WALK_IN_COUNT} clients" in text
    for hour in salon.APPOINTMENT_HOURS:
        assert f"{hour:02d}:00" in text
    assert "walk-in" in text.lower()


def test_r9_rules_list_every_service_and_price():
    text = rules_text()
    for service in salon.SERVICES:
        assert f"{service.name}: ${service.price}" in text


def test_r9_rules_give_the_full_step_order():
    text = rules_text()
    positions = [text.index(step.value) for step in (
        salon.Step.ASK_HEALTH, salon.Step.WASH_HANDS, salon.Step.WASH_FEET,
        salon.Step.REMOVE_PRODUCT, salon.Step.FILE, salon.Step.BUFF,
        salon.Step.POLISH)]
    assert positions == sorted(positions), "steps are not listed in order"


def test_r9_rules_explain_stars_and_the_goal():
    text = rules_text().lower()
    assert "star" in text
    assert f"${salon.DAILY_GOAL}" in text


def test_r9_rules_follow_the_game_settings(monkeypatch):
    monkeypatch.setattr(salon, "DAILY_GOAL", 999)
    assert "$999" in rules_text()


# --- Terminal: rules first, then the player chooses to begin --------------------

def test_r9_terminal_shows_rules_before_the_first_client(monkeypatch, capsys):
    prompts = []

    def fake_input(prompt=""):
        prompts.append(prompt)
        raise EOFError  # the player leaves at the very first prompt

    monkeypatch.setattr("builtins.input", fake_input)
    game.main(["--seed", "1"])
    out = capsys.readouterr().out
    for section in salon.rules():
        assert section.heading in out
        for line in section.lines:
            assert line in out
    assert "begin" in prompts[0].lower(), "first prompt should ask to begin"
    assert "APPOINTMENT" not in out and "WALK-IN" not in out, \
        "a client arrived before the player chose to begin"


def test_r9_terminal_starts_the_day_after_the_player_begins(monkeypatch, capsys):
    answers = iter([""])  # press Enter to begin, then leave

    def fake_input(prompt=""):
        try:
            return next(answers)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr("builtins.input", fake_input)
    game.main(["--seed", "1"])
    out = capsys.readouterr().out
    assert re.search(r"(APPOINTMENT|WALK-IN):", out), "no client after beginning"


# --- Browser: rules screen with a Begin button -------------------------------------

@pytest.fixture
def server():
    import web
    srv = web.make_server("127.0.0.1", 0, seed=1)
    thread = threading.Thread(target=srv.serve_forever, args=(0.05,), daemon=True)
    thread.start()
    host, port = srv.server_address[:2]
    yield f"http://{host}:{port}"
    srv.shutdown()
    srv.server_close()


def test_r9_server_sends_the_rules(server):
    with urllib.request.urlopen(server + "/api/rules") as resp:
        assert resp.status == 200
        data = json.loads(resp.read())
    assert data["sections"] == [
        {"heading": s.heading, "lines": list(s.lines)} for s in salon.rules()
    ]


def test_r9_page_has_a_rules_screen_with_a_begin_button():
    page = (STATIC / "index.html").read_text()
    assert 'id="rules"' in page
    assert 'id="begin"' in page


def test_r9_page_asks_server_for_rules_and_waits_for_begin():
    script = (STATIC / "app.js").read_text()
    assert '"/api/rules"' in script
    start = script.split("// --- Start")[-1]
    assert "newGame()" not in start, "the day starts before the player begins"
    assert re.search(r'\$\("begin"\)\.addEventListener\("click"', script)


def test_r9_rules_text_is_not_written_in_the_page():
    """R9: the rules come from salon.py, so no step label is typed into the page."""
    page = (STATIC / "index.html").read_text() + (STATIC / "app.js").read_text()
    for step in salon.Step:
        assert step.value not in page, f"{step.value!r} is written in the page"
