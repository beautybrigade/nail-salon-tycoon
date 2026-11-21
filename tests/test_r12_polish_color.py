"""R12: the player must pick the client's polish color off the polish wall,
right after buffing and right before polishing. A wrong color means no star."""

import json
from decimal import Decimal
import random
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

import game
import salon
import web
from helpers import make_client

S = salon.Step
PICK = S.PICK_COLOR
Pick = salon.Pick
STATIC = Path(__file__).resolve().parent.parent / "static"


def pick(color="Cherry Red"):
    return Pick(PICK, color)


def almond_file():
    return Pick(S.FILE, "almond")


# --- The correct sequence ----------------------------------------------------

def test_r12_step_is_called_pick_polish_color():
    assert PICK.value == "Pick polish color"


def test_r12_step_sits_between_buff_and_polish_in_the_menu():
    order = list(S)
    assert order.index(S.BUFF) + 1 == order.index(PICK) == order.index(S.POLISH) - 1


def test_r12_manicure_picks_the_clients_color_right_before_polish():
    client = make_client(salon.MANICURE, color="Grape")
    assert salon.required_steps(client) == [
        S.ASK_HEALTH, S.WASH_HANDS, almond_file(), S.NIP_CUTICLES, S.BUFF,
        Pick(PICK, "Grape"), S.POLISH,
    ]


def test_r12_pedicure_also_picks_the_color():
    client = make_client(salon.PEDICURE, has_product=True, color="Tangerine")
    assert salon.required_steps(client) == [
        S.ASK_HEALTH, S.WASH_FEET, S.REMOVE_PRODUCT, S.FILE, S.NIP_CUTICLES,
        S.BUFF, Pick(PICK, "Tangerine"), S.POLISH,
    ]


def test_r12_combo_picks_the_color_once_before_the_hands_polish():
    client = make_client(salon.COMBO, color="Turquoise")
    steps = salon.required_steps(client)
    assert steps == [
        S.ASK_HEALTH, S.WASH_HANDS, almond_file(), S.NIP_CUTICLES, S.BUFF,
        Pick(PICK, "Turquoise"), S.POLISH,                                   # hands
        S.WASH_FEET, S.FILE, S.NIP_CUTICLES, S.BUFF, S.POLISH,               # feet
    ]


@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
@pytest.mark.parametrize("has_product", [False, True])
@pytest.mark.parametrize("condition", [None, salon.DIABETES])
def test_r12_every_pick_comes_right_after_buff_and_right_before_polish(
        service, has_product, condition):
    steps = salon.required_steps(
        make_client(service, has_product=has_product, condition=condition))
    picks = [i for i, s in enumerate(steps) if salon.step_of(s) is PICK]
    assert len(picks) == 1
    i = picks[0]
    assert steps[i - 1] is S.BUFF and steps[i + 1] is S.POLISH
    assert steps[i] == pick("Cherry Red")


# --- Judging -------------------------------------------------------------------

@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
def test_r12_the_right_color_earns_the_star(service):
    client = make_client(service, color="Hot Pink")
    result = salon.finish_service(client, salon.required_steps(client))
    assert result.satisfied and result.stars == 1 and result.earned == service.price


@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
def test_r12_the_wrong_color_is_one_mistake_half_a_star(service):
    client = make_client(service, color="Hot Pink")
    steps = [pick("Lime Green") if salon.step_of(s) is PICK else s
             for s in salon.required_steps(client)]
    result = salon.finish_service(client, steps)
    # Round 6 (R5): a wrong color is one mistake, so half a star and half pay.
    assert not result.satisfied and result.mistakes == 1
    assert result.stars == Decimal("0.5") and result.earned == Decimal(service.price) / 2


def test_r12_skipping_the_pick_means_no_star():
    client = make_client(salon.MANICURE)
    steps = [s for s in salon.required_steps(client) if salon.step_of(s) is not PICK]
    assert not salon.finish_service(client, steps).satisfied


def test_r12_picking_before_buffing_means_no_star():
    client = make_client(salon.MANICURE)
    steps = [S.ASK_HEALTH, S.WASH_HANDS, almond_file(), S.NIP_CUTICLES,
             pick(), S.BUFF, S.POLISH]
    assert not salon.finish_service(client, steps).satisfied


def test_r12_picking_after_polishing_means_no_star():
    client = make_client(salon.MANICURE)
    steps = [S.ASK_HEALTH, S.WASH_HANDS, almond_file(), S.NIP_CUTICLES,
             S.BUFF, S.POLISH, pick()]
    assert not salon.finish_service(client, steps).satisfied


def test_r12_combo_picking_again_before_the_feet_means_no_star():
    client = make_client(salon.COMBO)
    steps = salon.required_steps(client)
    steps.insert(len(steps) - 1, pick())  # a second pick before the feet's Polish
    assert not salon.finish_service(client, steps).satisfied


def test_r12_a_pick_with_no_color_means_no_star():
    client = make_client(salon.MANICURE)
    steps = [S.ASK_HEALTH, S.WASH_HANDS, almond_file(), S.NIP_CUTICLES,
             S.BUFF, PICK, S.POLISH]
    assert not salon.finish_service(client, steps).satisfied


# --- Choosing a color --------------------------------------------------------------

@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
def test_r12_the_polish_wall_offers_every_color(service):
    client = make_client(service)
    assert salon.choices_for(client, [], PICK) == tuple(salon.POLISH_COLORS)


@pytest.mark.parametrize("step", [S.ASK_HEALTH, S.WASH_HANDS, S.WASH_FEET,
                                  S.REMOVE_PRODUCT, S.NIP_CUTICLES, S.BUFF, S.POLISH])
def test_r12_other_steps_ask_for_no_choice(step):
    assert salon.choices_for(make_client(salon.COMBO), [], step) == ()


def test_r12_a_pick_is_labelled_with_its_color():
    assert salon.move_label(pick("Grape")) == "Pick polish color (Grape)"
    assert salon.move_label(S.BUFF) == "Buff"


def test_r12_game_records_the_picked_color():
    g = salon.Game(random.Random(1))
    g.take_step(PICK, "Grape")
    assert g.steps == [pick("Grape")]


def test_r12_game_refuses_a_pick_without_a_color_from_the_wall():
    g = salon.Game(random.Random(1))
    with pytest.raises(ValueError):
        g.take_step(PICK)
    with pytest.raises(ValueError):
        g.take_step(PICK, "Plaid")
    with pytest.raises(ValueError):
        g.take_step(S.BUFF, "Grape")  # buffing takes no color
    assert g.steps == []


# --- The nails show the picked color -------------------------------------------------

def test_r12_picking_a_color_does_not_change_the_nails():
    client = make_client(salon.MANICURE)
    before = salon.nail_looks(client, [S.BUFF])
    after = salon.nail_looks(client, [S.BUFF, pick("Grape")])
    assert before == after


def test_r12_polish_paints_the_picked_color_even_when_wrong():
    client = make_client(salon.MANICURE, color="Hot Pink")
    looks = salon.nail_looks(client, [pick("Lime Green"), S.POLISH])
    assert looks[salon.HANDS].polish_color == "Lime Green"


def test_r12_the_latest_pick_is_the_one_painted():
    client = make_client(salon.MANICURE, color="Hot Pink")
    looks = salon.nail_looks(client, [pick("Lime Green"), pick("Grape"), S.POLISH])
    assert looks[salon.HANDS].polish_color == "Grape"


def test_r12_polishing_without_a_pick_uses_the_clients_color():
    client = make_client(salon.MANICURE, color="Hot Pink")
    assert salon.brush_color(client, []) == "Hot Pink"
    looks = salon.nail_looks(client, [S.POLISH])
    assert looks[salon.HANDS].polish_color == "Hot Pink"


def test_r12_combo_feet_are_polished_with_the_hands_bottle():
    client = make_client(salon.COMBO, color="Electric Blue")
    looks = salon.nail_looks(client, salon.required_steps(client))
    assert looks[salon.HANDS].polish_color == "Electric Blue"
    assert looks[salon.FEET].polish_color == "Electric Blue"


# --- The rules screen (R9) mentions the pick -------------------------------------------

def rules_text():
    return "\n".join(line for sec in salon.rules() for line in sec.lines)


def test_r12_rules_put_the_pick_between_buff_and_polish():
    line = next(l for l in rules_text().splitlines() if S.BUFF.value in l)
    assert line.index(S.BUFF.value) < line.index(PICK.value) < line.index(" then Polish")


def test_r12_rules_say_a_combo_picks_the_color_once():
    text = rules_text()
    assert "polish wall" in text
    assert "once" in text


# --- The terminal game -----------------------------------------------------------------

def test_r12_terminal_shows_the_color_the_client_wants():
    assert "Grape" in game.describe_client(make_client(salon.PEDICURE, color="Grape"))


def play(monkeypatch, capsys, client, answers):
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    result = game.run_service(client)
    return result, capsys.readouterr().out


def menu(step):
    return str(game.MENU.index(step) + 1)


def color_number(name):
    return str(list(salon.POLISH_COLORS).index(name) + 1)


def test_r12_terminal_asks_for_a_color_and_names_the_bottle(monkeypatch, capsys):
    client = make_client(salon.PEDICURE, color="Grape")
    _, out = play(monkeypatch, capsys, client,
                  [menu(PICK), color_number("Grape"), str(game.FINISH)])
    assert "Grape bottle" in out
    assert "Pick polish color (Grape)" in out


def test_r12_terminal_full_pedicure_with_the_right_color_earns_the_star(monkeypatch, capsys):
    client = make_client(salon.PEDICURE, color="Grape")
    answers = [menu(S.ASK_HEALTH), menu(S.WASH_FEET), menu(S.FILE),
               menu(S.NIP_CUTICLES), menu(S.BUFF), menu(PICK), color_number("Grape"),
               menu(S.POLISH), str(game.FINISH)]
    result, _ = play(monkeypatch, capsys, client, answers)
    assert result.satisfied


def test_r12_terminal_wrong_color_loses_the_star(monkeypatch, capsys):
    client = make_client(salon.PEDICURE, color="Grape")
    answers = [menu(S.ASK_HEALTH), menu(S.WASH_FEET), menu(S.FILE),
               menu(S.NIP_CUTICLES), menu(S.BUFF), menu(PICK), color_number("Hot Pink"),
               menu(S.POLISH), str(game.FINISH)]
    result, out = play(monkeypatch, capsys, client, answers)
    assert not result.satisfied
    assert "Pick polish color (Grape)" in out  # shown in "The correct steps were"


# --- The browser -------------------------------------------------------------------------

def test_r12_picking_has_its_own_animation():
    name = web.STEP_ANIMATIONS[PICK]
    assert name == "pick-color"
    others = [v for k, v in web.STEP_ANIMATIONS.items() if k is not PICK]
    assert name not in others
    assert f'"{name}"' in (STATIC / "app.js").read_text()
    assert f"@keyframes {name}" in (STATIC / "style.css").read_text()


def test_r12_page_draws_a_polish_wall():
    assert 'id="polish-wall"' in (STATIC / "index.html").read_text()


def test_r12_ninth_step_button_has_its_own_color():
    assert ".steps button:nth-child(9)" in (STATIC / "style.css").read_text()


@pytest.fixture
def server():
    srv = web.make_server("127.0.0.1", 0, seed=1)
    thread = threading.Thread(target=srv.serve_forever, args=(0.05,), daemon=True)
    thread.start()
    host, port = srv.server_address[:2]
    yield srv, f"http://{host}:{port}"
    srv.shutdown()
    srv.server_close()


def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def test_r12_server_asks_for_a_color_before_taking_the_step(server):
    srv, base = server
    start = post(base + "/api/new-game", {})
    assert "PICK_COLOR" in [s["id"] for s in start["steps"]]
    reply = post(base + "/api/step", {"game_id": start["game_id"], "step": "PICK_COLOR"})
    choose = reply["choose"]
    assert choose["step"] == "PICK_COLOR"
    assert [o["id"] for o in choose["options"]] == list(salon.POLISH_COLORS)
    assert choose["options"][0]["hex"] == salon.POLISH_COLORS[choose["options"][0]["id"]]
    assert srv.games[start["game_id"]].steps == [], "no step until a color is chosen"


def test_r12_server_takes_the_pick_and_returns_its_color(server):
    srv, base = server
    start = post(base + "/api/new-game", {})
    reply = post(base + "/api/step", {"game_id": start["game_id"],
                                      "step": "PICK_COLOR", "choice": "Grape"})
    assert reply["animation"] == "pick-color"
    assert reply["steps_taken"] == ["Pick polish color (Grape)"]
    assert reply["brush_hex"] == salon.POLISH_COLORS["Grape"]
    assert srv.games[start["game_id"]].steps == [pick("Grape")]


def test_r12_server_refuses_a_color_not_on_the_wall(server):
    _, base = server
    start = post(base + "/api/new-game", {})
    with pytest.raises(urllib.error.HTTPError) as err:
        post(base + "/api/step", {"game_id": start["game_id"],
                                  "step": "PICK_COLOR", "choice": "Plaid"})
    assert err.value.code == 400
