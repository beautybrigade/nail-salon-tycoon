"""Shared helpers for building clients in tests."""

import salon


def make_client(service, has_product=False, condition=None,
                hour=10, kind=salon.APPOINTMENT, color="Cherry Red"):
    return salon.Client(hour, kind, service, has_product, condition, color)
