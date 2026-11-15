"""R5: the client gives a star if satisfied, and the star decides if money is made."""

import pytest

import salon
from helpers import make_client

PRICES = [(salon.MANICURE, 25), (salon.PEDICURE, 35), (salon.COMBO, 55)]


@pytest.mark.parametrize("service,price", PRICES, ids=lambda x: getattr(x, "name", str(x)))
def test_r5_correct_steps_earn_a_star_and_full_price(service, price):
    client = make_client(service, has_product=True)
    result = salon.finish_service(client, salon.required_steps(client))
    assert result.satisfied
    assert result.stars == 1
    assert result.earned == price


@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
def test_r5_wrong_order_earns_no_star_and_no_money(service):
    client = make_client(service)
    steps = salon.required_steps(client)
    steps[-1], steps[-2] = steps[-2], steps[-1]  # polish before buff
    result = salon.finish_service(client, steps)
    assert not result.satisfied
    assert result.stars == 0
    assert result.earned == 0


def test_r5_finishing_with_no_steps_earns_nothing():
    result = salon.finish_service(make_client(salon.MANICURE), [])
    assert (result.stars, result.earned) == (0, 0)
