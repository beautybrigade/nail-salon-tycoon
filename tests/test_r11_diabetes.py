"""R11: if the client has diabetes, cuticle nipping is left out of the service.
Nipping a diabetic client's cuticles anyway is a mistake (student's decision)."""

from decimal import Decimal

import pytest

import game
import salon
from helpers import make_client

S = salon.Step
NIP = S.NIP_CUTICLES
DIABETES = "diabetes"


def test_r11_diabetes_is_one_of_the_health_conditions():
    assert DIABETES in salon.HEALTH_CONDITIONS


@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
@pytest.mark.parametrize("has_product", [False, True])
def test_r11_diabetic_client_needs_no_nipping(service, has_product):
    client = make_client(service, has_product=has_product, condition=DIABETES)
    assert NIP not in salon.required_steps(client)


def test_r11_diabetic_manicure_exact_steps():
    client = make_client(salon.MANICURE, condition=DIABETES)
    assert salon.required_steps(client) == [
        S.ASK_HEALTH, S.WASH_HANDS, salon.Pick(S.FILE, "almond"), S.BUFF,
        salon.Pick(S.PICK_COLOR, "Cherry Red"), S.POLISH,  # R12, R13 (round 5)
    ]


def test_r11_diabetic_combo_skips_nipping_on_hands_and_feet():
    client = make_client(salon.COMBO, has_product=True, condition=DIABETES)
    assert salon.required_steps(client) == [
        S.ASK_HEALTH, S.WASH_HANDS,
        S.REMOVE_PRODUCT, salon.Pick(S.FILE, "almond"), S.BUFF,
        salon.Pick(S.PICK_COLOR, "Cherry Red"), S.POLISH,  # R12, R13 (round 5)
        S.WASH_FEET,
        S.REMOVE_PRODUCT, S.FILE, S.BUFF, S.POLISH,
    ]


@pytest.mark.parametrize("condition", ["sensitive skin", "allergic to acetone", None])
def test_r11_other_conditions_still_need_nipping(condition):
    client = make_client(salon.PEDICURE, condition=condition)
    assert NIP in salon.required_steps(client)


def test_r11_diabetic_client_without_nipping_earns_the_star():
    client = make_client(salon.PEDICURE, condition=DIABETES)
    steps = [S.ASK_HEALTH, S.WASH_FEET, S.FILE, S.BUFF,
             salon.Pick(S.PICK_COLOR, "Cherry Red"), S.POLISH]  # R12 (round 5)
    result = salon.finish_service(client, steps)
    assert result.satisfied and result.earned == salon.PEDICURE.price


@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
def test_r11_nipping_a_diabetic_client_is_one_mistake(service):
    client = make_client(service, condition=DIABETES)
    steps = salon.required_steps(client)
    first_file = [salon.step_of(s) for s in steps].index(S.FILE)
    steps.insert(first_file + 1, NIP)  # where it goes for others
    result = salon.finish_service(client, steps)
    # Round 6 (R5): one mistake now earns half a star and half the price.
    assert not result.satisfied and result.mistakes == 1
    assert result.earned == Decimal(service.price) / 2


def test_r11_diabetic_client_says_so_when_asked():
    client = make_client(salon.MANICURE, condition=DIABETES)
    assert DIABETES in salon.health_answer(client)


def test_r11_rules_say_never_to_nip_a_diabetic_client():
    text = "\n".join(line for sec in salon.rules() for line in sec.lines)
    nip_line = next(line for line in text.splitlines() if NIP.value in line)
    assert DIABETES in nip_line.lower()


def test_r11_terminal_shows_the_right_steps_for_a_diabetic_client(monkeypatch, capsys):
    """A diabetic client who gets nipped is unsatisfied, and the terminal's
    list of correct steps has no nipping in it."""
    client = make_client(salon.MANICURE, condition=DIABETES)
    picks = [S.ASK_HEALTH, S.WASH_HANDS, S.FILE, NIP, S.BUFF, S.POLISH]
    answers = [str(game.MENU.index(s) + 1) for s in picks] + [str(game.FINISH)]
    answers.insert(3, str(salon.NAIL_SHAPES.index("almond") + 1))  # R13: File asks
    choices = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(choices))
    result = game.run_service(client)
    out = capsys.readouterr().out
    assert not result.satisfied
    correct_line = next(l for l in out.splitlines() if "correct steps" in l)
    assert NIP.value not in correct_line
