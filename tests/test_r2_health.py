"""R2: ask the client about special health conditions before the service."""

import pytest

import salon
from helpers import make_client


@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
def test_r2_health_question_comes_first_for_every_service(service):
    assert salon.required_steps(make_client(service))[0] is salon.Step.ASK_HEALTH


def test_r2_health_question_asked_only_once_even_for_combo():
    steps = salon.required_steps(make_client(salon.COMBO, has_product=True))
    assert steps.count(salon.Step.ASK_HEALTH) == 1


def test_r2_skipping_health_question_makes_client_unsatisfied():
    client = make_client(salon.PEDICURE)
    steps = [s for s in salon.required_steps(client) if s is not salon.Step.ASK_HEALTH]
    assert not salon.finish_service(client, steps).satisfied


def test_r2_asking_health_question_late_makes_client_unsatisfied():
    client = make_client(salon.PEDICURE)
    steps = salon.required_steps(client)[1:] + [salon.Step.ASK_HEALTH]
    assert not salon.finish_service(client, steps).satisfied


def test_r2_client_reports_their_condition():
    assert "diabetes" in salon.health_answer(make_client(salon.MANICURE, condition="diabetes"))


def test_r2_client_without_condition_says_none():
    assert salon.health_answer(make_client(salon.MANICURE)) == "No conditions."
