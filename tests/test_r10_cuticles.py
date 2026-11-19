"""R10: nipping the cuticles is a new part of every service. It comes after
filing and right before buffing, in both the terminal and the browser."""

import json
import threading
import urllib.request
from pathlib import Path

import pytest

import game
import salon
import web
from helpers import make_client

S = salon.Step
NIP = S.NIP_CUTICLES
STATIC = Path(__file__).resolve().parent.parent / "static"


# --- The correct sequence ----------------------------------------------------

def test_r10_step_is_called_nip_cuticles():
    assert NIP.value == "Nip cuticles"


def test_r10_manicure_nips_between_file_and_buff():
    steps = [salon.step_of(s) for s in salon.required_steps(make_client(salon.MANICURE))]
    assert steps == [S.ASK_HEALTH, S.WASH_HANDS, S.FILE, NIP, S.BUFF,
                     S.PICK_COLOR, S.POLISH]  # PICK_COLOR: R12 (round 5)


@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
@pytest.mark.parametrize("has_product", [False, True])
def test_r10_every_nip_comes_right_after_file_and_right_before_buff(service, has_product):
    steps = [salon.step_of(s)  # round 5: the hands' File carries a shape (R13)
             for s in salon.required_steps(make_client(service, has_product=has_product))]
    nip_positions = [i for i, s in enumerate(steps) if s is NIP]
    assert len(nip_positions) == len(service.areas)
    for i in nip_positions:
        assert steps[i - 1] is S.FILE and steps[i + 1] is S.BUFF


def test_r10_combo_nips_both_hands_and_feet():
    steps = [salon.step_of(s)
             for s in salon.required_steps(make_client(salon.COMBO, has_product=True))]
    assert steps == [
        S.ASK_HEALTH, S.WASH_HANDS,
        S.REMOVE_PRODUCT, S.FILE, NIP, S.BUFF, S.PICK_COLOR, S.POLISH,   # hands
        S.WASH_FEET,
        S.REMOVE_PRODUCT, S.FILE, NIP, S.BUFF, S.POLISH,   # feet
    ]


# --- Mistakes ----------------------------------------------------------------

def test_r10_doing_every_step_with_nipping_earns_the_star():
    client = make_client(salon.PEDICURE)
    result = salon.finish_service(client, salon.required_steps(client))
    assert result.satisfied and result.earned == salon.PEDICURE.price


@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
def test_r10_skipping_nipping_makes_client_unsatisfied(service):
    client = make_client(service)
    steps = [s for s in salon.required_steps(client) if s is not NIP]
    assert not salon.finish_service(client, steps).satisfied


def test_r10_combo_nipping_only_the_hands_makes_client_unsatisfied():
    client = make_client(salon.COMBO)
    steps = salon.required_steps(client)
    last_nip = len(steps) - 1 - steps[::-1].index(NIP)
    del steps[last_nip]
    assert not salon.finish_service(client, steps).satisfied


def test_r10_nipping_before_filing_makes_client_unsatisfied():
    client = make_client(salon.MANICURE)
    steps = [S.ASK_HEALTH, S.WASH_HANDS, NIP, S.FILE, S.BUFF, S.POLISH]
    assert not salon.finish_service(client, steps).satisfied


def test_r10_nipping_after_buffing_makes_client_unsatisfied():
    client = make_client(salon.MANICURE)
    steps = [S.ASK_HEALTH, S.WASH_HANDS, S.FILE, S.BUFF, NIP, S.POLISH]
    assert not salon.finish_service(client, steps).satisfied


def test_r10_nipping_twice_makes_client_unsatisfied():
    client = make_client(salon.MANICURE)
    steps = [S.ASK_HEALTH, S.WASH_HANDS, S.FILE, NIP, NIP, S.BUFF, S.POLISH]
    assert not salon.finish_service(client, steps).satisfied


# --- The nails change (R8 look for the new step) --------------------------------

def test_r10_nails_start_with_cuticles_not_nipped():
    look = salon.nail_looks(make_client(salon.MANICURE), [])[salon.HANDS]
    assert not look.cuticles_nipped


def test_r10_nipping_tidies_the_cuticles_and_changes_nothing_else():
    client = make_client(salon.MANICURE)
    filed = salon.nail_looks(client, [S.ASK_HEALTH, S.WASH_HANDS, S.FILE])
    nipped = salon.nail_looks(client, [S.ASK_HEALTH, S.WASH_HANDS, S.FILE, NIP])
    assert nipped[salon.HANDS].cuticles_nipped
    assert nipped[salon.HANDS].filed
    assert not nipped[salon.HANDS].buffed
    assert nipped[salon.HANDS].polish_color is None
    assert not filed[salon.HANDS].cuticles_nipped


def test_r10_combo_nipping_the_feet_leaves_the_hands_as_they_were():
    client = make_client(salon.COMBO)
    steps = salon.required_steps(client)
    hands_done = steps[:steps.index(S.POLISH) + 1]
    looks = salon.nail_looks(client, hands_done + [S.WASH_FEET, S.FILE])
    assert looks[salon.HANDS].cuticles_nipped
    assert not looks[salon.FEET].cuticles_nipped
    looks = salon.nail_looks(client, hands_done + [S.WASH_FEET, S.FILE, NIP])
    assert looks[salon.FEET].cuticles_nipped


# --- The rules screen (R9) mentions the new step ---------------------------------

def rules_text():
    return "\n".join(line for sec in salon.rules() for line in sec.lines)


def test_r10_rules_put_nipping_between_file_and_buff():
    text = rules_text()
    assert text.index(S.FILE.value) < text.index(NIP.value) < text.index(S.BUFF.value)


# --- The browser ---------------------------------------------------------------------

def test_r10_nipping_has_its_own_animation():
    name = web.STEP_ANIMATIONS[NIP]
    assert name == "nip-cuticles"
    others = [v for k, v in web.STEP_ANIMATIONS.items() if k is not NIP]
    assert name not in others
    assert f'"{name}"' in (STATIC / "app.js").read_text()
    assert f"@keyframes {name}" in (STATIC / "style.css").read_text()


def test_r10_page_draws_cuticle_nippers():
    assert 'id="nippers"' in (STATIC / "index.html").read_text()


def test_r10_server_sends_nipping_animation_and_nail_look():
    srv = web.make_server("127.0.0.1", 0, seed=1)
    thread = threading.Thread(target=srv.serve_forever, args=(0.05,), daemon=True)
    thread.start()
    host, port = srv.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        start = post(base + "/api/new-game", {})
        reply = post(base + "/api/step",
                     {"game_id": start["game_id"], "step": "NIP_CUTICLES"})
    finally:
        srv.shutdown()
        srv.server_close()
    assert "NIP_CUTICLES" in [s["id"] for s in start["steps"]]
    assert reply["animation"] == "nip-cuticles"
    assert reply["label"] == NIP.value
    area = reply["working_area"]
    assert reply["nails"][area]["cuticles_nipped"] is True
    assert start["client"]["nails"][area]["cuticles_nipped"] is False


def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# --- The terminal game ------------------------------------------------------------

def test_r10_terminal_menu_offers_nipping_between_file_and_buff():
    assert game.MENU.index(S.FILE) < game.MENU.index(NIP) < game.MENU.index(S.BUFF)


def test_r10_terminal_says_the_cuticles_are_nipped(monkeypatch, capsys):
    client = make_client(salon.MANICURE)
    choices = iter([str(game.MENU.index(NIP) + 1), str(game.FINISH)])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(choices))
    game.run_service(client)
    assert "nip the cuticles" in capsys.readouterr().out
