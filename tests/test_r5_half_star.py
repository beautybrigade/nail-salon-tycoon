"""R5 (changed in round 6): exactly one mistake earns half a star and half the
price; two or more mistakes earn nothing.

Student's answers: any one mistake counts (a skipped, extra, wrong, or moved
step), safety mistakes count the same, cents are kept, and a combo is judged
as one service."""

import json
import random
import threading
import urllib.request
from decimal import Decimal
from pathlib import Path

import pytest

import game
import salon
import web
from helpers import make_client

S = salon.Step
STATIC = Path(__file__).resolve().parent.parent / "static"
HALF = {salon.MANICURE.name: Decimal("12.50"),
        salon.PEDICURE.name: Decimal("17.50"),
        salon.COMBO.name: Decimal("27.50")}
by_name = lambda s: getattr(s, "name", str(s))


def without(steps, step):
    """The steps with the first move of this step left out."""
    i = [salon.step_of(m) for m in steps].index(step)
    return steps[:i] + steps[i + 1:]


# --- Counting mistakes --------------------------------------------------------

@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_exact_steps_have_no_mistakes(service):
    client = make_client(service, has_product=True)
    assert salon.count_mistakes(client, salon.required_steps(client)) == 0


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
@pytest.mark.parametrize("has_product", [False, True])
def test_r5_any_one_skipped_step_is_one_mistake(service, has_product):
    client = make_client(service, has_product=has_product)
    steps = salon.required_steps(client)
    for i in range(len(steps)):
        skipped = steps[:i] + steps[i + 1:]
        assert salon.count_mistakes(client, skipped) == 1, f"skipped step {i}"


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
@pytest.mark.parametrize("extra", [S.WASH_HANDS, S.REMOVE_PRODUCT, S.BUFF, S.ASK_HEALTH])
def test_r5_one_extra_step_anywhere_is_one_mistake(service, extra):
    client = make_client(service)
    steps = salon.required_steps(client)
    for i in range(len(steps) + 1):
        assert salon.count_mistakes(client, steps[:i] + [extra] + steps[i:]) == 1


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_one_wrong_step_in_place_of_a_right_one_is_one_mistake(service):
    client = make_client(service)
    steps = salon.required_steps(client)
    steps[1] = S.REMOVE_PRODUCT  # instead of washing
    assert salon.count_mistakes(client, steps) == 1


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_a_wrong_color_is_one_mistake(service):
    client = make_client(service, color="Hot Pink")
    steps = [salon.Pick(S.PICK_COLOR, "Lime Green") if salon.step_of(m) is S.PICK_COLOR
             else m for m in salon.required_steps(client)]
    assert salon.count_mistakes(client, steps) == 1


@pytest.mark.parametrize("service", [salon.MANICURE, salon.COMBO], ids=by_name)
def test_r5_a_wrong_shape_is_one_mistake(service):
    client = make_client(service, shape="round")
    steps = [salon.Pick(S.FILE, "square") if m == salon.Pick(S.FILE, "round") else m
             for m in salon.required_steps(client)]
    assert salon.count_mistakes(client, steps) == 1


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_two_steps_swapped_side_by_side_is_one_mistake(service):
    client = make_client(service)
    steps = salon.required_steps(client)
    steps[-1], steps[-2] = steps[-2], steps[-1]
    assert salon.count_mistakes(client, steps) == 1


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_one_step_moved_far_away_is_one_mistake(service):
    """The student's answer: one step done in the wrong place is one mistake,
    even when it moved far (here the health question is asked last)."""
    client = make_client(service, has_product=True)
    steps = salon.required_steps(client)
    moved = steps[1:] + steps[:1]
    assert salon.count_mistakes(client, moved) == 1
    moved_back = steps[-1:] + steps[:-1]  # polish first
    assert salon.count_mistakes(client, moved_back) == 1


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_two_skipped_steps_are_two_mistakes(service):
    client = make_client(service)
    steps = without(without(salon.required_steps(client), S.BUFF), S.ASK_HEALTH)
    assert salon.count_mistakes(client, steps) == 2


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_a_skipped_step_and_a_wrong_color_are_two_mistakes(service):
    client = make_client(service, color="Hot Pink")
    steps = [salon.Pick(S.PICK_COLOR, "Lime Green") if salon.step_of(m) is S.PICK_COLOR
             else m for m in salon.required_steps(client)]
    assert salon.count_mistakes(client, without(steps, S.ASK_HEALTH)) == 2


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_two_separate_swaps_are_two_mistakes(service):
    client = make_client(service)
    steps = salon.required_steps(client)
    steps[0], steps[1] = steps[1], steps[0]
    steps[-1], steps[-2] = steps[-2], steps[-1]
    assert salon.count_mistakes(client, steps) == 2


def test_r5_one_skipped_and_one_extra_step_are_two_mistakes():
    client = make_client(salon.MANICURE)
    steps = without(salon.required_steps(client), S.BUFF) + [S.REMOVE_PRODUCT]
    assert salon.count_mistakes(client, steps) == 2


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_no_steps_at_all_are_two_or_more_mistakes(service):
    assert salon.count_mistakes(make_client(service), []) == 2


# --- Stars and pay --------------------------------------------------------------

@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_one_mistake_earns_half_a_star_and_exactly_half_the_price(service):
    client = make_client(service, has_product=True)
    result = salon.finish_service(client, without(salon.required_steps(client), S.BUFF))
    assert result.mistakes == 1
    assert not result.satisfied
    assert result.stars == Decimal("0.5")
    assert result.earned == HALF[service.name]
    assert isinstance(result.earned, Decimal), "money is kept as an exact Decimal"


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_no_mistakes_still_earn_a_full_star_and_full_price(service):
    client = make_client(service)
    result = salon.finish_service(client, salon.required_steps(client))
    assert (result.mistakes, result.satisfied) == (0, True)
    assert result.stars == 1 and result.earned == service.price


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_two_mistakes_earn_no_star_and_nothing(service):
    client = make_client(service)
    steps = without(without(salon.required_steps(client), S.BUFF), S.ASK_HEALTH)
    result = salon.finish_service(client, steps)
    assert (result.mistakes, result.satisfied, result.stars, result.earned) == (2, False, 0, 0)


@pytest.mark.parametrize("service", salon.SERVICES, ids=by_name)
def test_r5_skipping_only_the_health_question_still_earns_half(service):
    """Student's answer: safety mistakes count like any other mistake."""
    client = make_client(service)
    result = salon.finish_service(client, without(salon.required_steps(client), S.ASK_HEALTH))
    assert result.stars == Decimal("0.5") and result.earned == HALF[service.name]


def test_r5_nipping_only_a_diabetic_clients_cuticles_still_earns_half():
    """Student's answer: nipping a diabetic client is one mistake like any other."""
    client = make_client(salon.MANICURE, condition="diabetes")
    steps = salon.required_steps(client)
    file_at = [salon.step_of(m) for m in steps].index(S.FILE)
    steps.insert(file_at + 1, S.NIP_CUTICLES)
    result = salon.finish_service(client, steps)
    assert result.stars == Decimal("0.5") and result.earned == Decimal("12.50")


def test_r5_combo_one_mistake_on_the_feet_earns_half_the_combo():
    client = make_client(salon.COMBO)
    steps = salon.required_steps(client)
    last_buff = max(i for i, m in enumerate(steps) if m is S.BUFF)
    del steps[last_buff]  # the feet's buff
    assert salon.finish_service(client, steps).earned == Decimal("27.50")


def test_r5_combo_one_mistake_on_hands_and_one_on_feet_earns_nothing():
    """Student's answer: a combo is one service, so its mistakes add up."""
    client = make_client(salon.COMBO)
    steps = salon.required_steps(client)
    buffs = [i for i, m in enumerate(steps) if m is S.BUFF]
    assert len(buffs) == 2
    steps = [m for i, m in enumerate(steps) if i not in buffs]
    result = salon.finish_service(client, steps)
    assert result.mistakes == 2 and result.earned == 0


# --- End of the day and money text ----------------------------------------------

def half_result(service):
    client = make_client(service)
    return salon.finish_service(client, without(salon.required_steps(client), S.BUFF))


def full_result(service):
    client = make_client(service)
    return salon.finish_service(client, salon.required_steps(client))


def test_r5_day_total_keeps_the_cents():
    day = salon.end_of_day([full_result(salon.COMBO)] * 2
                           + [half_result(salon.PEDICURE), half_result(salon.MANICURE)])
    assert day.total == Decimal("140.00")  # 55 + 55 + 17.50 + 12.50
    day = salon.end_of_day([full_result(salon.COMBO)] * 2 + [half_result(salon.PEDICURE)])
    assert day.total == Decimal("127.50")
    assert not day.goal_met


def test_r5_half_pay_can_reach_the_goal_exactly():
    day = salon.end_of_day([full_result(salon.MANICURE)] * 5 + [half_result(salon.MANICURE)] * 2)
    assert day.total == 150 and day.goal_met  # 125 + 12.50 + 12.50


def test_r5_half_pay_just_below_the_goal_does_not_meet_it():
    day = salon.end_of_day([full_result(salon.COMBO)] * 2 + [full_result(salon.MANICURE)]
                           + [half_result(salon.MANICURE)])
    assert day.total == Decimal("147.50") and not day.goal_met  # 55 + 55 + 25 + 12.50


@pytest.mark.parametrize("amount,text", [
    (0, "$0"), (25, "$25"), (Decimal("12.50"), "$12.50"), (Decimal("12.5"), "$12.50"),
    (Decimal("142.50"), "$142.50"), (Decimal("150.00"), "$150"),
])
def test_r5_money_shows_cents_only_when_there_are_cents(amount, text):
    assert salon.money(amount) == text


def test_r5_rules_explain_full_half_and_no_pay():
    text = "\n".join(line for section in salon.rules() for line in section.lines).lower()
    assert "half a star" in text and "half the price" in text
    assert "two or more" in text


# --- Terminal -------------------------------------------------------------------

def answers_for(client, moves):
    """What the player types in the terminal to take these moves, then Finish."""
    answers, taken = [], []
    for move in moves:
        step = salon.step_of(move)
        answers.append(str(game.MENU.index(step) + 1))
        if isinstance(move, salon.Pick):
            options = salon.choices_for(client, taken, step)
            answers.append(str(list(options).index(move.choice) + 1))
        taken.append(move)
    return answers + [str(game.FINISH)]


def test_r5_terminal_one_mistake_shows_half_a_star_and_the_correct_steps(monkeypatch, capsys):
    client = make_client(salon.MANICURE)
    answers = iter(answers_for(client, without(salon.required_steps(client), S.BUFF)))
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    result = game.run_service(client)
    out = capsys.readouterr().out
    assert result.earned == Decimal("12.50")
    assert "Half a star" in out and "+$12.50" in out
    assert "correct steps" in out


def test_r5_terminal_two_mistakes_show_no_star(monkeypatch, capsys):
    client = make_client(salon.MANICURE)
    moves = without(without(salon.required_steps(client), S.BUFF), S.ASK_HEALTH)
    answers = iter(answers_for(client, moves))
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    game.run_service(client)
    out = capsys.readouterr().out
    assert "No star, no payment" in out and "Half a star" not in out


def test_r5_terminal_summary_shows_half_stars_and_cents(capsys):
    day = salon.end_of_day([full_result(salon.COMBO), half_result(salon.PEDICURE),
                            salon.finish_service(make_client(salon.MANICURE), [])])
    game.print_summary(day)
    out = capsys.readouterr().out
    lines = out.splitlines()
    combo = next(l for l in lines if salon.COMBO.name in l)
    pedi = next(l for l in lines if salon.PEDICURE.name in l)
    mani = next(l for l in lines if salon.MANICURE.name in l)
    assert "★" in combo and "$55" in combo
    assert "½" in pedi and "$17.50" in pedi
    assert "–" in mani and "$0" in mani
    assert "Total earnings: $72.50" in out


# --- Browser --------------------------------------------------------------------

SEED = 3


@pytest.fixture
def server():
    srv = web.make_server("127.0.0.1", 0, seed=SEED)
    thread = threading.Thread(target=srv.serve_forever, args=(0.05,), daemon=True)
    thread.start()
    host, port = srv.server_address[:2]
    yield f"http://{host}:{port}"
    srv.shutdown()
    srv.server_close()


def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def play(server, game_id, moves):
    for move in moves:
        body = {"game_id": game_id, "step": salon.step_of(move).name}
        if isinstance(move, salon.Pick):
            body["choice"] = move.choice
        post(server + "/api/step", body)
    return post(server + "/api/finish", {"game_id": game_id})


def test_r5_browser_one_mistake_sends_half_a_star_and_half_pay(server):
    first = salon.generate_day(random.Random(SEED))[0]
    game_id = post(server + "/api/new-game", {})["game_id"]
    done = play(server, game_id, without(salon.required_steps(first), S.ASK_HEALTH))
    assert done["result"] == {"satisfied": False, "stars": 0.5, "mistakes": 1,
                              "earned": first.service.price / 2}
    assert done["correct_steps"] == [salon.move_label(m) for m in salon.required_steps(first)]
    assert done["total_so_far"] == first.service.price / 2
    assert done["stars_so_far"] == 0.5


def test_r5_browser_day_of_half_stars_totals_the_cents(server):
    clients = salon.generate_day(random.Random(SEED))
    game_id = post(server + "/api/new-game", {})["game_id"]
    for client in clients:
        done = play(server, game_id, without(salon.required_steps(client), S.BUFF))
    total = sum(Decimal(c.service.price) / 2 for c in clients)
    assert done["day"]["total"] == float(total)
    assert done["day"]["goal_met"] == (total >= salon.DAILY_GOAL)
    assert [r["stars"] for r in done["day"]["results"]] == [0.5] * 6
    assert done["stars_so_far"] == 3


def test_r5_page_shows_half_stars_and_cents():
    """The page draws a half star and writes cents; it does not work out pay."""
    js = (STATIC / "app.js").read_text()
    assert "½" in js
    assert "toFixed(2)" in js
    assert "stars_so_far" in js
    assert "price / 2" not in js and "price/2" not in js
