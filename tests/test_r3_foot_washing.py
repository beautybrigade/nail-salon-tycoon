"""R3 (changed in round 3): pedicures get a foot-washing step, judged like
hand washing, with its own washing animation in the browser."""

import json
import threading
import urllib.request
from pathlib import Path

import game
import salon
import web
from helpers import make_client

S = salon.Step
FEET_WASH = S.WASH_FEET
STATIC = Path(__file__).resolve().parent.parent / "static"


# --- The correct sequence ----------------------------------------------------

def test_r3_pedicure_requires_foot_washing_right_after_health():
    steps = salon.required_steps(make_client(salon.PEDICURE))
    assert steps == [S.ASK_HEALTH, FEET_WASH, S.FILE, S.NIP_CUTICLES,  # R10
                     S.BUFF, salon.Pick(S.PICK_COLOR, "Cherry Red"),  # R12
                     S.POLISH]


def test_r3_pedicure_washes_feet_before_removing_product():
    steps = salon.required_steps(make_client(salon.PEDICURE, has_product=True))
    assert steps[:3] == [S.ASK_HEALTH, FEET_WASH, S.REMOVE_PRODUCT]


def test_r3_manicure_does_not_require_foot_washing():
    assert FEET_WASH not in salon.required_steps(make_client(salon.MANICURE))


def test_r3_combo_washes_feet_once_after_the_hands_are_polished():
    steps = salon.required_steps(make_client(salon.COMBO, has_product=True))
    assert steps.count(FEET_WASH) == 1
    first_polish = steps.index(S.POLISH)
    assert steps.index(FEET_WASH) == first_polish + 1
    assert steps[first_polish + 1:] == [FEET_WASH, S.REMOVE_PRODUCT,
                                        S.FILE, S.NIP_CUTICLES,  # R10
                                        S.BUFF, S.POLISH]


# --- Mistakes ----------------------------------------------------------------

def test_r3_skipping_foot_washing_on_pedicure_makes_client_unsatisfied():
    client = make_client(salon.PEDICURE)
    steps = [s for s in salon.required_steps(client) if s is not FEET_WASH]
    assert not salon.finish_service(client, steps).satisfied


def test_r3_doing_the_pedicure_steps_in_order_earns_the_star():
    client = make_client(salon.PEDICURE, has_product=True)
    result = salon.finish_service(client, salon.required_steps(client))
    assert result.satisfied and result.earned == salon.PEDICURE.price


def test_r3_foot_washing_on_manicure_makes_client_unsatisfied():
    client = make_client(salon.MANICURE)
    steps = salon.required_steps(client)
    steps.insert(2, FEET_WASH)
    assert not salon.finish_service(client, steps).satisfied


def test_r3_washing_feet_before_the_hands_in_combo_makes_client_unsatisfied():
    client = make_client(salon.COMBO)
    steps = [s for s in salon.required_steps(client) if s is not FEET_WASH]
    steps.insert(2, FEET_WASH)  # right after hand washing, before the hands
    assert not salon.finish_service(client, steps).satisfied


def test_r3_hand_washing_instead_of_foot_washing_makes_client_unsatisfied():
    client = make_client(salon.PEDICURE)
    steps = [S.WASH_HANDS if s is FEET_WASH else s
             for s in salon.required_steps(client)]
    assert not salon.finish_service(client, steps).satisfied


# --- Nails and the shown area ---------------------------------------------------

def test_r3_washing_feet_does_not_change_the_nails():
    client = make_client(salon.PEDICURE, has_product=True)
    assert (salon.nail_looks(client, [S.ASK_HEALTH, FEET_WASH])
            == salon.nail_looks(client, []))


def test_r3_combo_shows_the_feet_when_they_are_washed():
    client = make_client(salon.COMBO)
    steps = salon.required_steps(client)
    before_feet_wash = steps[:steps.index(FEET_WASH)]
    assert salon.working_area(client, before_feet_wash) == salon.FEET


# --- The washing animation (browser) -------------------------------------------

def test_r3_foot_washing_has_its_own_animation():
    name = web.STEP_ANIMATIONS[FEET_WASH]
    assert name == "wash-feet"
    assert name != web.STEP_ANIMATIONS[S.WASH_HANDS]
    assert f'"{name}"' in (STATIC / "app.js").read_text()
    assert f"@keyframes {name}" in (STATIC / "style.css").read_text()


def test_r3_page_draws_a_foot_bath():
    assert 'id="foot-bath"' in (STATIC / "index.html").read_text()


def test_r3_server_sends_the_foot_washing_animation():
    srv = web.make_server("127.0.0.1", 0, seed=1)
    thread = threading.Thread(target=srv.serve_forever, args=(0.05,), daemon=True)
    thread.start()
    host, port = srv.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        game_id = post(base + "/api/new-game", {})["game_id"]
        reply = post(base + "/api/step", {"game_id": game_id, "step": "WASH_FEET"})
    finally:
        srv.shutdown()
        srv.server_close()
    assert reply["animation"] == "wash-feet"
    assert reply["label"] == FEET_WASH.value


def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# --- The terminal game ------------------------------------------------------------

def test_r3_terminal_menu_offers_foot_washing():
    assert FEET_WASH in game.MENU


def test_r3_terminal_says_the_feet_are_soaking(monkeypatch, capsys):
    client = make_client(salon.PEDICURE)
    choices = iter([str(game.MENU.index(FEET_WASH) + 1), str(game.FINISH)])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(choices))
    game.run_service(client)
    assert "feet soak" in capsys.readouterr().out
