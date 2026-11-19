"""R13: manicure and combo clients choose a nail shape (square, round,
stiletto, or almond). Filing the hands must use that shape, the nails show the
shape they were filed into, and a wrong shape means no star. Pedicures, and
the feet of a combo, have no shape."""

import json
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
Pick = salon.Pick
STATIC = Path(__file__).resolve().parent.parent / "static"
SHAPES = ("square", "round", "stiletto", "almond")


def shaped(shape):
    return Pick(S.FILE, shape)


# --- Clients choose a shape ----------------------------------------------------

def test_r13_the_four_shapes():
    assert salon.NAIL_SHAPES == SHAPES


def test_r13_hand_service_clients_choose_a_shape_and_pedicures_do_not():
    for seed in range(40):
        for client in salon.generate_day(random.Random(seed)):
            if client.service.is_hand_service:
                assert client.nail_shape in SHAPES
            else:
                assert client.nail_shape is None


def test_r13_every_shape_comes_up():
    seen = {c.nail_shape for seed in range(60)
            for c in salon.generate_day(random.Random(seed))}
    assert seen == set(SHAPES) | {None}


def test_r13_the_same_seed_gives_the_same_shapes():
    first = [c.nail_shape for c in salon.generate_day(random.Random(7))]
    again = [c.nail_shape for c in salon.generate_day(random.Random(7))]
    assert first == again


# --- The correct sequence ----------------------------------------------------------

@pytest.mark.parametrize("shape", SHAPES)
def test_r13_manicure_files_into_the_clients_shape(shape):
    steps = salon.required_steps(make_client(salon.MANICURE, shape=shape))
    files = [s for s in steps if salon.step_of(s) is S.FILE]
    assert files == [shaped(shape)]


def test_r13_shaping_happens_with_filing_right_after_product_removal():
    steps = salon.required_steps(make_client(salon.MANICURE, has_product=True,
                                             shape="square"))
    i = steps.index(shaped("square"))
    assert steps[i - 1] is S.REMOVE_PRODUCT
    assert steps[i + 1] is S.NIP_CUTICLES


def test_r13_pedicure_files_with_no_shape():
    steps = salon.required_steps(make_client(salon.PEDICURE))
    files = [s for s in steps if salon.step_of(s) is S.FILE]
    assert files == [S.FILE]


def test_r13_combo_shapes_only_the_hands():
    steps = salon.required_steps(make_client(salon.COMBO, shape="stiletto"))
    files = [s for s in steps if salon.step_of(s) is S.FILE]
    assert files == [shaped("stiletto"), S.FILE]


# --- Judging -------------------------------------------------------------------------

@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("service", [salon.MANICURE, salon.COMBO], ids=lambda s: s.name)
def test_r13_the_right_shape_earns_the_star(service, shape):
    client = make_client(service, shape=shape)
    result = salon.finish_service(client, salon.required_steps(client))
    assert result.satisfied and result.earned == service.price


@pytest.mark.parametrize("service", [salon.MANICURE, salon.COMBO], ids=lambda s: s.name)
def test_r13_the_wrong_shape_means_no_star(service):
    client = make_client(service, shape="round")
    steps = [shaped("stiletto") if s == shaped("round") else s
             for s in salon.required_steps(client)]
    result = salon.finish_service(client, steps)
    assert not result.satisfied and result.stars == 0 and result.earned == 0


def test_r13_filing_the_hands_with_no_shape_means_no_star():
    client = make_client(salon.MANICURE, shape="round")
    steps = [S.FILE if s == shaped("round") else s for s in salon.required_steps(client)]
    assert not salon.finish_service(client, steps).satisfied


def test_r13_shaping_a_pedicure_means_no_star():
    client = make_client(salon.PEDICURE)
    steps = [shaped("almond") if s is S.FILE else s for s in salon.required_steps(client)]
    assert not salon.finish_service(client, steps).satisfied


def test_r13_shaping_the_feet_of_a_combo_means_no_star():
    client = make_client(salon.COMBO, shape="almond")
    steps = salon.required_steps(client)
    feet_file = len(steps) - 1 - steps[::-1].index(S.FILE)
    steps[feet_file] = shaped("almond")
    assert not salon.finish_service(client, steps).satisfied


# --- Choosing a shape -------------------------------------------------------------------

def test_r13_filing_the_hands_asks_for_a_shape():
    client = make_client(salon.MANICURE)
    assert salon.choices_for(client, [S.ASK_HEALTH, S.WASH_HANDS], S.FILE) == SHAPES


def test_r13_filing_a_pedicure_asks_for_nothing():
    assert salon.choices_for(make_client(salon.PEDICURE), [], S.FILE) == ()


def test_r13_combo_asks_for_a_shape_on_the_hands_only():
    client = make_client(salon.COMBO)
    steps = salon.required_steps(client)
    hands_done = steps[:steps.index(S.POLISH) + 1]
    assert salon.choices_for(client, [], S.FILE) == SHAPES
    assert salon.choices_for(client, hands_done + [S.WASH_FEET], S.FILE) == ()


def test_r13_a_shaped_file_is_labelled_with_its_shape():
    assert salon.move_label(shaped("almond")) == "File (almond)"
    assert salon.move_label(S.FILE) == "File"


def first_client_with(test):
    for seed in range(200):
        day = salon.generate_day(random.Random(seed))
        if test(day[0]):
            return seed
    raise AssertionError("no seed found")


def test_r13_game_asks_for_a_shape_only_when_filing_hands():
    seed = first_client_with(lambda c: c.service.is_hand_service)
    g = salon.Game(random.Random(seed))
    with pytest.raises(ValueError):
        g.take_step(S.FILE)
    with pytest.raises(ValueError):
        g.take_step(S.FILE, "heart")
    g.take_step(S.FILE, "square")
    assert g.steps == [shaped("square")]

    seed = first_client_with(lambda c: c.service is salon.PEDICURE)
    g = salon.Game(random.Random(seed))
    with pytest.raises(ValueError):
        g.take_step(S.FILE, "square")
    g.take_step(S.FILE)
    assert g.steps == [S.FILE]


# --- The nails show the shape -----------------------------------------------------------

def test_r13_nails_have_no_shape_before_filing():
    look = salon.nail_looks(make_client(salon.MANICURE), [S.ASK_HEALTH])[salon.HANDS]
    assert look.shape is None and not look.filed


@pytest.mark.parametrize("shape", SHAPES)
def test_r13_nails_show_the_shape_they_were_filed_into(shape):
    client = make_client(salon.MANICURE, shape="almond")
    look = salon.nail_looks(client, [shaped(shape)])[salon.HANDS]
    assert look.filed and look.shape == shape


def test_r13_plain_filing_the_feet_gives_no_shape():
    look = salon.nail_looks(make_client(salon.PEDICURE), [S.FILE])[salon.FEET]
    assert look.filed and look.shape is None


def test_r13_combo_hands_keep_their_shape_while_the_feet_are_filed():
    client = make_client(salon.COMBO, shape="stiletto")
    looks = salon.nail_looks(client, salon.required_steps(client))
    assert looks[salon.HANDS].shape == "stiletto"
    assert looks[salon.FEET].shape is None and looks[salon.FEET].filed


# --- The rules screen (R9) mentions the shape --------------------------------------------

def test_r13_rules_name_the_four_shapes():
    text = "\n".join(line for sec in salon.rules() for line in sec.lines)
    for shape in SHAPES:
        assert shape in text


# --- The terminal game ----------------------------------------------------------------------

def test_r13_terminal_shows_the_shape_the_client_wants():
    assert "stiletto" in game.describe_client(make_client(salon.MANICURE, shape="stiletto"))
    assert "shape" not in game.describe_client(make_client(salon.PEDICURE))


def play(monkeypatch, capsys, client, answers):
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    result = game.run_service(client)
    return result, capsys.readouterr().out


def menu(step):
    return str(game.MENU.index(step) + 1)


def shape_number(shape):
    return str(SHAPES.index(shape) + 1)


def test_r13_terminal_asks_for_the_shape_when_filing_hands(monkeypatch, capsys):
    client = make_client(salon.MANICURE, shape="almond")
    _, out = play(monkeypatch, capsys, client,
                  [menu(S.FILE), shape_number("almond"), str(game.FINISH)])
    assert "almond shape" in out
    assert "File (almond)" in out


def test_r13_terminal_does_not_ask_for_a_shape_on_a_pedicure(monkeypatch, capsys):
    client = make_client(salon.PEDICURE)
    _, out = play(monkeypatch, capsys, client, [menu(S.FILE), str(game.FINISH)])
    assert "shape" not in out


def test_r13_terminal_full_manicure_with_the_right_shape_earns_the_star(monkeypatch, capsys):
    client = make_client(salon.MANICURE, shape="square", color="Grape")
    answers = [menu(S.ASK_HEALTH), menu(S.WASH_HANDS), menu(S.FILE), shape_number("square"),
               menu(S.NIP_CUTICLES), menu(S.BUFF), menu(S.PICK_COLOR),
               str(list(salon.POLISH_COLORS).index("Grape") + 1),
               menu(S.POLISH), str(game.FINISH)]
    result, _ = play(monkeypatch, capsys, client, answers)
    assert result.satisfied


# --- The browser ------------------------------------------------------------------------------

def test_r13_page_draws_every_shape():
    css = (STATIC / "style.css").read_text()
    js = (STATIC / "app.js").read_text()
    for shape in SHAPES:
        assert f".shape-{shape}" in css
    assert "look.shape" in js


@pytest.fixture
def server_for():
    servers = []

    def start(seed):
        srv = web.make_server("127.0.0.1", 0, seed=seed)
        threading.Thread(target=srv.serve_forever, args=(0.05,), daemon=True).start()
        servers.append(srv)
        host, port = srv.server_address[:2]
        return f"http://{host}:{port}"
    yield start
    for srv in servers:
        srv.shutdown()
        srv.server_close()


def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def test_r13_server_asks_for_a_shape_and_draws_it(server_for):
    seed = first_client_with(lambda c: c.service is salon.MANICURE)
    base = server_for(seed)
    start = post(base + "/api/new-game", {})
    wanted = salon.generate_day(random.Random(seed))[0].nail_shape
    assert start["client"]["nail_shape"] == wanted
    assert start["client"]["nails"]["hands"]["shape"] is None

    reply = post(base + "/api/step", {"game_id": start["game_id"], "step": "FILE"})
    assert reply["choose"]["step"] == "FILE"
    assert [o["id"] for o in reply["choose"]["options"]] == list(SHAPES)

    reply = post(base + "/api/step", {"game_id": start["game_id"],
                                      "step": "FILE", "choice": "stiletto"})
    assert reply["animation"] == "file-nails"
    assert reply["nails"]["hands"]["shape"] == "stiletto"
    assert reply["steps_taken"] == ["File (stiletto)"]


def test_r13_server_files_a_pedicure_without_asking(server_for):
    seed = first_client_with(lambda c: c.service is salon.PEDICURE)
    base = server_for(seed)
    start = post(base + "/api/new-game", {})
    assert start["client"]["nail_shape"] is None
    reply = post(base + "/api/step", {"game_id": start["game_id"], "step": "FILE"})
    assert "choose" not in reply
    assert reply["nails"]["feet"]["filed"] is True


def test_r13_server_refuses_an_unknown_shape(server_for):
    seed = first_client_with(lambda c: c.service is salon.MANICURE)
    base = server_for(seed)
    start = post(base + "/api/new-game", {})
    with pytest.raises(urllib.error.HTTPError) as err:
        post(base + "/api/step", {"game_id": start["game_id"],
                                  "step": "FILE", "choice": "heart"})
    assert err.value.code == 400
