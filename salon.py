"""Game logic for Nail Salon Tycoon.

This module holds every rule of the game and never talks to the terminal:
no input() and no print(). All randomness comes from a random.Random that the
caller passes in, so a seeded Random always produces the same day.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

# --- Day settings (see spec.md) -------------------------------------------

OPEN_HOUR = 9
LAST_SLOT_HOUR = 16  # the last one-hour slot starts at 16:00; closes at 17:00
APPOINTMENT_HOURS = (10, 12, 14)
WALK_IN_COUNT = 3
DAILY_GOAL = 150
PRODUCT_CHANCE = 0.5
HEALTH_CONDITION_CHANCE = 0.3
HEALTH_CONDITIONS = ("sensitive skin", "diabetes", "allergic to acetone")

APPOINTMENT = "appointment"
WALK_IN = "walk-in"


# --- Steps and services ----------------------------------------------------

class Step(Enum):
    """Something the player can do during a service. The value is the menu label."""

    ASK_HEALTH = "Ask about health conditions"
    WASH_HANDS = "Ask client to wash hands"
    REMOVE_PRODUCT = "Remove product"
    FILE = "File"
    BUFF = "Buff"
    POLISH = "Polish"


HANDS = "hands"
FEET = "feet"


@dataclass(frozen=True)
class Service:
    name: str
    price: int
    areas: tuple[str, ...]  # worked on in this order

    @property
    def is_hand_service(self) -> bool:
        return HANDS in self.areas


MANICURE = Service("Manicure", 25, (HANDS,))
PEDICURE = Service("Pedicure", 35, (FEET,))
COMBO = Service("Mani + Pedi combo", 55, (HANDS, FEET))
SERVICES = (MANICURE, PEDICURE, COMBO)


# --- Clients and the day ---------------------------------------------------

@dataclass(frozen=True)
class Client:
    hour: int
    kind: str  # APPOINTMENT or WALK_IN
    service: Service
    has_product: bool
    health_condition: str | None  # None means no conditions


def _random_client(rng: random.Random, hour: int, kind: str) -> Client:
    service = rng.choice(SERVICES)
    has_product = rng.random() < PRODUCT_CHANCE
    condition = (
        rng.choice(HEALTH_CONDITIONS)
        if rng.random() < HEALTH_CONDITION_CHANCE
        else None
    )
    return Client(hour, kind, service, has_product, condition)


def free_hours() -> list[int]:
    """Hours in the day that have no appointment, so a walk-in can arrive then."""
    return [
        h for h in range(OPEN_HOUR, LAST_SLOT_HOUR + 1)
        if h not in APPOINTMENT_HOURS
    ]


def generate_day(rng: random.Random) -> list[Client]:
    """R1: build the day's clients: fixed appointments plus random walk-ins.

    Appointments are always at APPOINTMENT_HOURS. Walk-ins arrive at distinct
    random free hours. The list is sorted by hour, the order clients are served.
    """
    clients = [_random_client(rng, h, APPOINTMENT) for h in APPOINTMENT_HOURS]
    walk_in_hours = rng.sample(free_hours(), WALK_IN_COUNT)
    clients += [_random_client(rng, h, WALK_IN) for h in walk_in_hours]
    return sorted(clients, key=lambda c: c.hour)


# --- Rules for a single service --------------------------------------------

def health_answer(client: Client) -> str:
    """R2: what the client says when asked about health conditions."""
    if client.health_condition is None:
        return "No conditions."
    return f"Yes: {client.health_condition}."


def required_steps(client: Client) -> list[Step]:
    """R2, R3, R4: the one correct sequence of steps for this client."""
    steps = [Step.ASK_HEALTH]
    for area in client.service.areas:
        if area == HANDS:
            steps.append(Step.WASH_HANDS)
        if client.has_product:
            steps.append(Step.REMOVE_PRODUCT)
        steps += [Step.FILE, Step.BUFF, Step.POLISH]
    return steps


@dataclass(frozen=True)
class ServiceResult:
    client: Client
    satisfied: bool
    stars: int
    earned: int


def finish_service(client: Client, steps_taken: list[Step]) -> ServiceResult:
    """R5: judge the player's steps. A star (and the full price) only if exact."""
    satisfied = list(steps_taken) == required_steps(client)
    stars = 1 if satisfied else 0
    earned = client.service.price if satisfied else 0
    return ServiceResult(client, satisfied, stars, earned)


# --- End of the day ---------------------------------------------------------

@dataclass(frozen=True)
class DayResult:
    results: tuple[ServiceResult, ...]
    total: int
    goal: int
    goal_met: bool


def end_of_day(results: list[ServiceResult], goal: int = DAILY_GOAL) -> DayResult:
    """R6: total the day's earnings and check them against the daily goal."""
    total = sum(r.earned for r in results)
    return DayResult(tuple(results), total, goal, total >= goal)
