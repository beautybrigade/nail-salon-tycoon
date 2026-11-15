"""R3: ask the client to wash hands before hand services, not for pedicures."""

import salon
from helpers import make_client

WASH = salon.Step.WASH_HANDS


def test_r3_manicure_requires_hand_washing_before_nail_work():
    steps = salon.required_steps(make_client(salon.MANICURE))
    assert steps[:2] == [salon.Step.ASK_HEALTH, WASH]


def test_r3_pedicure_does_not_require_hand_washing():
    assert WASH not in salon.required_steps(make_client(salon.PEDICURE))


def test_r3_combo_washes_hands_once_before_the_hands():
    steps = salon.required_steps(make_client(salon.COMBO))
    assert steps.count(WASH) == 1
    assert steps.index(WASH) == 1


def test_r3_skipping_hand_washing_on_manicure_makes_client_unsatisfied():
    client = make_client(salon.MANICURE)
    steps = [s for s in salon.required_steps(client) if s is not WASH]
    assert not salon.finish_service(client, steps).satisfied


def test_r3_hand_washing_on_pedicure_makes_client_unsatisfied():
    client = make_client(salon.PEDICURE)
    steps = salon.required_steps(client)
    steps.insert(1, WASH)
    assert not salon.finish_service(client, steps).satisfied


def test_r3_hand_washing_before_feet_part_of_combo_makes_client_unsatisfied():
    client = make_client(salon.COMBO)
    steps = salon.required_steps(client)
    steps.insert(5, WASH)  # after the hands' polish, before the feet
    assert not salon.finish_service(client, steps).satisfied


def test_r3_service_knows_whether_it_is_a_hand_service():
    assert salon.MANICURE.is_hand_service
    assert salon.COMBO.is_hand_service
    assert not salon.PEDICURE.is_hand_service
