"""R7: the game is playable in a browser on the player's own computer and
starts with one command (python3 web.py)."""

import http.server
import json
import random
import threading
import urllib.error
import urllib.request

import pytest

import salon
import web

SEED = 3


# --- A Game walks through one day (used by the browser) ---------------------

def test_r7_game_serves_the_days_clients_in_order():
    game = salon.Game(random.Random(SEED))
    expected = salon.generate_day(random.Random(SEED))
    seen = []
    while not game.is_over:
        seen.append(game.current_client)
        game.finish()
    assert seen == expected
    assert game.current_client is None


def test_r7_game_judges_steps_like_round_one():
    game = salon.Game(random.Random(SEED))
    client = game.current_client
    for step in salon.required_steps(client):
        game.take_step(step)
    result = game.finish()
    assert result.satisfied and result.earned == client.service.price
    assert game.steps == [], "steps should reset for the next client"
    assert game.finish().earned == 0, "finishing with no steps earns nothing"


def test_r7_game_end_of_day_totals_earnings():
    game = salon.Game(random.Random(SEED))
    while not game.is_over:
        for step in salon.required_steps(game.current_client):
            game.take_step(step)
        game.finish()
    day = game.day_result()
    total = sum(c.service.price for c in salon.generate_day(random.Random(SEED)))
    assert day.total == total
    assert day.goal_met == (total >= salon.DAILY_GOAL)


def test_r7_game_refuses_steps_after_the_day_is_over():
    game = salon.Game(random.Random(SEED))
    while not game.is_over:
        game.finish()
    with pytest.raises(ValueError):
        game.take_step(salon.Step.FILE)
    with pytest.raises(ValueError):
        game.finish()


# --- The local web server ---------------------------------------------------

@pytest.fixture
def server():
    srv = web.make_server("127.0.0.1", 0, seed=SEED)
    thread = threading.Thread(target=srv.serve_forever, args=(0.05,), daemon=True)
    thread.start()
    host, port = srv.server_address[:2]
    yield f"http://{host}:{port}"
    srv.shutdown()
    srv.server_close()


def get(url):
    with urllib.request.urlopen(url) as resp:
        return resp.status, resp.headers.get("Content-Type", ""), resp.read().decode()


def post(url, data):
    req = urllib.request.Request(
        url, data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def test_r7_server_listens_only_on_this_computer():
    srv = web.make_server(web.HOST, 0)
    try:
        assert srv.server_address[0] == "127.0.0.1"
    finally:
        srv.server_close()


def test_r7_home_page_is_the_game(server):
    status, ctype, body = get(server + "/")
    assert status == 200 and ctype.startswith("text/html")
    assert "Nail Salon Tycoon" in body
    assert "/static/app.js" in body and "/static/style.css" in body


@pytest.mark.parametrize("name,ctype", [
    ("app.js", "text/javascript"), ("style.css", "text/css"),
])
def test_r7_page_files_are_served(server, name, ctype):
    status, got_type, _ = get(f"{server}/static/{name}")
    assert status == 200 and got_type.startswith(ctype)


@pytest.mark.parametrize("path", ["/static/../salon.py", "/static/%2e%2e/salon.py",
                                  "/nope", "/static/missing.js"])
def test_r7_only_page_files_are_served(server, path):
    with pytest.raises(urllib.error.HTTPError) as err:
        get(server + path)
    assert err.value.code == 404


def test_r7_new_game_sends_first_client_and_step_menu(server):
    status, data = post(server + "/api/new-game", {})
    assert status == 200
    first = salon.generate_day(random.Random(SEED))[0]
    client = data["client"]
    assert client["hour"] == first.hour and client["kind"] == first.kind
    assert client["service"] == first.service.name
    assert client["price"] == first.service.price
    assert client["polish_color"] == first.polish_color
    assert client["polish_hex"] == salon.POLISH_COLORS[first.polish_color]
    assert data["client_number"] == 1 and data["total_clients"] == 6
    assert data["goal"] == salon.DAILY_GOAL
    assert [s["label"] for s in data["steps"]] == [s.value for s in salon.Step]


def test_r7_full_day_played_over_the_browser_interface(server):
    clients = salon.generate_day(random.Random(SEED))
    _, data = post(server + "/api/new-game", {})
    game_id = data["game_id"]
    for i, client in enumerate(clients):
        for move in salon.required_steps(client):
            body = {"game_id": game_id, "step": salon.step_of(move).name}
            if isinstance(move, salon.Pick):  # round 5: a color or shape (R12, R13)
                body["choice"] = move.choice
            status, reply = post(server + "/api/step", body)
            assert status == 200 and "choose" not in reply
        _, done = post(server + "/api/finish", {"game_id": game_id})
        assert done["result"]["stars"] == 1
        assert done["result"]["earned"] == client.service.price
        if i < len(clients) - 1:
            assert done["next_client"]["hour"] == clients[i + 1].hour
            assert done["day"] is None
    total = sum(c.service.price for c in clients)
    assert done["next_client"] is None
    assert done["day"]["total"] == total
    assert done["day"]["goal_met"] == (total >= salon.DAILY_GOAL)
    assert len(done["day"]["results"]) == 6


def test_r7_wrong_steps_earn_nothing_and_show_the_correct_steps(server):
    _, data = post(server + "/api/new-game", {})
    post(server + "/api/step", {"game_id": data["game_id"], "step": "POLISH"})
    _, done = post(server + "/api/finish", {"game_id": data["game_id"]})
    first = salon.generate_day(random.Random(SEED))[0]
    assert done["result"] == {"satisfied": False, "stars": 0, "earned": 0,
                              "mistakes": 2}  # round 6: 2 means "two or more"
    assert done["correct_steps"] == [salon.move_label(s)  # round 5: with choices
                                     for s in salon.required_steps(first)]


def test_r7_health_question_gets_the_clients_answer(server):
    _, data = post(server + "/api/new-game", {})
    _, reply = post(server + "/api/step", {"game_id": data["game_id"], "step": "ASK_HEALTH"})
    first = salon.generate_day(random.Random(SEED))[0]
    assert reply["health_answer"] == salon.health_answer(first)


def test_r7_step_reply_includes_animation_and_nails(server):
    _, data = post(server + "/api/new-game", {})
    _, reply = post(server + "/api/step", {"game_id": data["game_id"], "step": "FILE"})
    if "choose" in reply:  # round 5: filing the hands asks for a shape (R13)
        _, reply = post(server + "/api/step", {"game_id": data["game_id"], "step": "FILE",
                                               "choice": salon.NAIL_SHAPES[0]})
    assert reply["animation"] == web.STEP_ANIMATIONS[salon.Step.FILE]
    area = reply["working_area"]
    assert reply["nails"][area]["filed"] is True


@pytest.mark.parametrize("path,body", [
    ("/api/step", {"game_id": "x", "step": "FILE"}),
    ("/api/finish", {"game_id": "x"}),
])
def test_r7_unknown_game_is_an_error(server, path, body):
    status, data = post(server + path, body)
    assert status == 400 and "error" in data


def test_r7_unknown_step_is_an_error(server):
    _, data = post(server + "/api/new-game", {})
    status, reply = post(server + "/api/step", {"game_id": data["game_id"], "step": "DANCE"})
    assert status == 400 and "error" in reply


# --- One command starts it and opens the browser ----------------------------

@pytest.fixture
def no_serving(monkeypatch):
    """Let main() run without blocking forever or opening a real browser."""
    monkeypatch.setattr(http.server.ThreadingHTTPServer, "serve_forever",
                        lambda self, *a, **k: None)
    opened = []
    monkeypatch.setattr(web.webbrowser, "open", lambda url, *a, **k: opened.append(url))
    return opened


def test_r7_one_command_opens_the_game_in_the_browser(no_serving):
    srv = web.main(["--port", "0"])
    host, port = srv.server_address[:2]
    assert no_serving == [f"http://{host}:{port}/"]


def test_r7_no_browser_flag_skips_opening(no_serving):
    web.main(["--port", "0", "--no-browser"])
    assert no_serving == []


def test_r7_busy_port_falls_back_to_a_free_one(no_serving):
    busy = web.make_server(web.HOST, 0)
    try:
        taken = busy.server_address[1]
        srv = web.main(["--port", str(taken), "--no-browser"])
        assert srv.server_address[1] != taken
    finally:
        busy.server_close()
