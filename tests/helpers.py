"""Shared helpers for building clients in tests."""

import salon

_DEFAULT = object()


def make_client(service, has_product=False, condition=None,
                hour=10, kind=salon.APPOINTMENT, color="Cherry Red",
                shape=_DEFAULT):
    """A client for tests. Hand services get the almond shape unless a shape
    is given (R13); pedicures get no shape."""
    if shape is _DEFAULT:
        shape = "almond" if service.is_hand_service else None
    return salon.Client(hour, kind, service, has_product, condition, color,
                        nail_shape=shape)
