"""R1: walk-ins show up randomly; appointments come at set times."""

import random

import salon

SEEDS = range(50)


def walk_ins(day):
    return [c for c in day if c.kind == salon.WALK_IN]


def appointments(day):
    return [c for c in day if c.kind == salon.APPOINTMENT]


def test_r1_appointments_are_at_set_times_every_day():
    for seed in SEEDS:
        day = salon.generate_day(random.Random(seed))
        assert [c.hour for c in appointments(day)] == [10, 12, 14]


def test_r1_day_has_six_clients_three_of_each_kind():
    day = salon.generate_day(random.Random(0))
    assert len(day) == 6
    assert len(appointments(day)) == 3
    assert len(walk_ins(day)) == 3


def test_r1_walk_ins_arrive_at_distinct_free_hours():
    for seed in SEEDS:
        hours = [c.hour for c in walk_ins(salon.generate_day(random.Random(seed)))]
        assert len(set(hours)) == 3
        assert set(hours) <= {9, 11, 13, 15, 16}


def test_r1_walk_in_hours_vary_from_day_to_day():
    patterns = {
        tuple(c.hour for c in walk_ins(salon.generate_day(random.Random(s))))
        for s in SEEDS
    }
    assert len(patterns) > 1


def test_r1_same_seed_gives_same_day():
    assert salon.generate_day(random.Random(7)) == salon.generate_day(random.Random(7))


def test_r1_clients_are_served_in_time_order():
    for seed in SEEDS:
        hours = [c.hour for c in salon.generate_day(random.Random(seed))]
        assert hours == sorted(hours)
