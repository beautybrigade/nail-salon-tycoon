"""R4: every service needs filing, buffing, polishing; product removal first if needed."""

import pytest

import salon
from helpers import make_client

S = salon.Step


def test_r4_manicure_without_product_exact_steps():
    assert salon.required_steps(make_client(salon.MANICURE)) == [
        S.ASK_HEALTH, S.WASH_HANDS, S.FILE, S.NIP_CUTICLES, S.BUFF, S.POLISH,
    ]  # R10 (round 4): cuticles are nipped between filing and buffing


def test_r4_pedicure_with_product_starts_with_removal():
    # R3 (round 3): the feet are washed before the nail work starts.
    # R10 (round 4): cuticles are nipped between filing and buffing.
    assert salon.required_steps(make_client(salon.PEDICURE, has_product=True)) == [
        S.ASK_HEALTH, S.WASH_FEET, S.REMOVE_PRODUCT, S.FILE, S.NIP_CUTICLES,
        S.BUFF, S.POLISH,
    ]


def test_r4_combo_with_product_does_both_areas_in_order():
    assert salon.required_steps(make_client(salon.COMBO, has_product=True)) == [
        S.ASK_HEALTH, S.WASH_HANDS,
        S.REMOVE_PRODUCT, S.FILE, S.NIP_CUTICLES, S.BUFF, S.POLISH,   # hands
        S.WASH_FEET,                                  # R3 (round 3)
        S.REMOVE_PRODUCT, S.FILE, S.NIP_CUTICLES, S.BUFF, S.POLISH,   # feet
        # NIP_CUTICLES: R10 (round 4)
    ]


@pytest.mark.parametrize("service", salon.SERVICES, ids=lambda s: s.name)
def test_r4_no_removal_when_client_has_no_product(service):
    assert S.REMOVE_PRODUCT not in salon.required_steps(make_client(service))


def test_r4_skipping_removal_when_product_is_on_makes_client_unsatisfied():
    client = make_client(salon.MANICURE, has_product=True)
    steps = [s for s in salon.required_steps(client) if s is not S.REMOVE_PRODUCT]
    assert not salon.finish_service(client, steps).satisfied


def test_r4_removing_product_that_is_not_there_makes_client_unsatisfied():
    client = make_client(salon.PEDICURE)
    steps = salon.required_steps(client)
    steps.insert(1, S.REMOVE_PRODUCT)
    assert not salon.finish_service(client, steps).satisfied


@pytest.mark.parametrize("missing", [S.FILE, S.BUFF, S.POLISH])
def test_r4_skipping_file_buff_or_polish_makes_client_unsatisfied(missing):
    client = make_client(salon.PEDICURE)
    steps = [s for s in salon.required_steps(client) if s is not missing]
    assert not salon.finish_service(client, steps).satisfied


def test_r4_buffing_before_filing_makes_client_unsatisfied():
    client = make_client(salon.PEDICURE)
    steps = [S.ASK_HEALTH, S.BUFF, S.FILE, S.POLISH]
    assert not salon.finish_service(client, steps).satisfied


def test_r4_repeating_a_step_makes_client_unsatisfied():
    client = make_client(salon.PEDICURE)
    steps = salon.required_steps(client) + [S.POLISH]
    assert not salon.finish_service(client, steps).satisfied
