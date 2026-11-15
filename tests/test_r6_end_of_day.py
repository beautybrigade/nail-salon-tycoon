"""R6: at the end of the day, show total earnings and whether the goal was met."""

import random

import salon
from helpers import make_client


def result(service, satisfied):
    client = make_client(service)
    steps = salon.required_steps(client) if satisfied else []
    return salon.finish_service(client, steps)


def test_r6_daily_goal_is_150():
    assert salon.DAILY_GOAL == 150
    assert salon.end_of_day([]).goal == 150


def test_r6_total_adds_only_satisfied_services():
    day = salon.end_of_day([
        result(salon.MANICURE, True),   # 25
        result(salon.COMBO, True),      # 55
        result(salon.PEDICURE, False),  # 0
    ])
    assert day.total == 80
    assert not day.goal_met


def test_r6_goal_met_when_total_exactly_equals_goal():
    exactly = salon.end_of_day([result(salon.MANICURE, True)] * 6)  # 6 * 25 = 150
    assert exactly.total == 150
    assert exactly.goal_met


def test_r6_goal_not_met_just_below_goal():
    day = salon.end_of_day([result(salon.MANICURE, True)] * 5 + [result(salon.MANICURE, False)])
    assert day.total == 125
    assert not day.goal_met


def test_r6_perfect_day_earns_sum_of_all_prices():
    clients = salon.generate_day(random.Random(3))
    results = [salon.finish_service(c, salon.required_steps(c)) for c in clients]
    day = salon.end_of_day(results)
    assert day.total == sum(c.service.price for c in clients)
    assert len(day.results) == 6
