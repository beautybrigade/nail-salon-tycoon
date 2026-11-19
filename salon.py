"""Game logic for Nail Salon Tycoon.

This module holds every rule of the game and never talks to the terminal:
no input() and no print(). All randomness comes from a random.Random that the
caller passes in, so a seeded Random always produces the same day.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from enum import Enum

# --- Day settings (see spec.md) -------------------------------------------

OPEN_HOUR = 9
LAST_SLOT_HOUR = 16  # the last one-hour slot starts at 16:00; closes at 17:00
APPOINTMENT_HOURS = (10, 12, 14)
WALK_IN_COUNT = 3
DAILY_GOAL = 150
PRODUCT_CHANCE = 0.5
HEALTH_CONDITION_CHANCE = 0.3
DIABETES = "diabetes"  # R11: no cuticle nipping for these clients
HEALTH_CONDITIONS = ("sensitive skin", DIABETES, "allergic to acetone")

# R8: bright polish colors a client can ask for (name -> hex color for drawing)
POLISH_COLORS = {
    "Cherry Red": "#e0115f",
    "Hot Pink": "#ff3fa4",
    "Tangerine": "#ff8c1a",
    "Sunny Yellow": "#ffd60a",
    "Lime Green": "#7bd629",
    "Turquoise": "#1cc7c1",
    "Electric Blue": "#2f6bff",
    "Grape": "#8e44ec",
}

APPOINTMENT = "appointment"
WALK_IN = "walk-in"


# --- Steps and services ----------------------------------------------------

class Step(Enum):
    """Something the player can do during a service. The value is the menu label."""

    ASK_HEALTH = "Ask about health conditions"
    WASH_HANDS = "Ask client to wash hands"
    WASH_FEET = "Wash feet in foot bath"  # R3, round 3
    REMOVE_PRODUCT = "Remove product"
    FILE = "File"
    NIP_CUTICLES = "Nip cuticles"  # R10, round 4
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
    polish_color: str = "Cherry Red"  # R8: a name from POLISH_COLORS


def _random_client(rng: random.Random, hour: int, kind: str) -> Client:
    service = rng.choice(SERVICES)
    has_product = rng.random() < PRODUCT_CHANCE
    condition = (
        rng.choice(HEALTH_CONDITIONS)
        if rng.random() < HEALTH_CONDITION_CHANCE
        else None
    )
    color = rng.choice(list(POLISH_COLORS))
    return Client(hour, kind, service, has_product, condition, color)


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
    """R2, R3, R4: the one correct sequence of steps for this client.

    Each area is washed just before it is worked on: hands with WASH_HANDS,
    feet with WASH_FEET (R3 as changed in round 3). Each area's cuticles are
    nipped after filing and before buffing (R10), except for a client with
    diabetes (R11).
    """
    nip = [] if client.health_condition == DIABETES else [Step.NIP_CUTICLES]
    steps = [Step.ASK_HEALTH]
    for area in client.service.areas:
        steps.append(Step.WASH_HANDS if area == HANDS else Step.WASH_FEET)
        if client.has_product:
            steps.append(Step.REMOVE_PRODUCT)
        steps += [Step.FILE, *nip, Step.BUFF, Step.POLISH]
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


# --- What the nails look like (R8) ------------------------------------------

@dataclass(frozen=True)
class NailLook:
    """How one area's nails look right now, so the browser can draw them."""

    has_product: bool          # old polish still on
    filed: bool
    buffed: bool
    polish_color: str | None   # None until polished
    cuticles_nipped: bool = False  # R10: ragged cuticles until nipped


def _area_index(client: Client, steps_taken: list[Step]) -> int:
    """Which area the next step works on. Each Polish finishes an area."""
    polishes = sum(1 for s in steps_taken if s is Step.POLISH)
    return min(polishes, len(client.service.areas) - 1)


def working_area(client: Client, steps_taken: list[Step]) -> str:
    """R8: the area shown now: hands, or feet after the first Polish in a combo."""
    return client.service.areas[_area_index(client, steps_taken)]


def nail_looks(client: Client, steps_taken: list[Step]) -> dict[str, NailLook]:
    """R8: replay the player's steps and return each area's nail look.

    This shows what the player did, right or wrong; judging happens only in
    finish_service. Asking about health and washing do not change nails.
    """
    looks = {
        area: NailLook(client.has_product, False, False, None)
        for area in client.service.areas
    }
    done: list[Step] = []
    for step in steps_taken:
        area = working_area(client, done)
        look = looks[area]
        if step is Step.REMOVE_PRODUCT:
            look = replace(look, has_product=False)
        elif step is Step.FILE:
            look = replace(look, filed=True)
        elif step is Step.NIP_CUTICLES:
            look = replace(look, cuticles_nipped=True)
        elif step is Step.BUFF:
            look = replace(look, buffed=True)
        elif step is Step.POLISH:
            look = replace(look, polish_color=client.polish_color)
        looks[area] = look
        done.append(step)
    return looks


# --- The rules shown before the day begins (R9) ----------------------------

@dataclass(frozen=True)
class RuleSection:
    heading: str
    lines: tuple[str, ...]


def rules() -> list[RuleSection]:
    """R9: the rules of the day, built from the same settings the game uses.

    Both the terminal and the browser show this text, so it is written once.
    """
    appointments = ", ".join(f"{h:02d}:00" for h in APPOINTMENT_HOURS)
    clients = len(APPOINTMENT_HOURS) + WALK_IN_COUNT
    return [
        RuleSection("Your day", (
            f"The salon is open from {OPEN_HOUR:02d}:00 to "
            f"{LAST_SLOT_HOUR + 1:02d}:00. You will see {clients} clients, "
            "one at a time.",
            f"{len(APPOINTMENT_HOURS)} clients have appointments at "
            f"{appointments}.",
            f"{WALK_IN_COUNT} walk-in clients show up at random times.",
        )),
        RuleSection("Services", tuple(
            f"{s.name}: ${s.price}"
            + (" (hands first, then feet)" if len(s.areas) > 1 else "")
            for s in SERVICES
        )),
        RuleSection("Steps, in this order", (
            f"1. {Step.ASK_HEALTH.value}, first, for every client.",
            "2. Then for each area (hands first in a combo):",
            f'   a. Wash it: "{Step.WASH_HANDS.value}" for the hands, '
            f'"{Step.WASH_FEET.value}" for the feet.',
            f"   b. {Step.REMOVE_PRODUCT.value}, only if the client has old "
            "polish on.",
            f"   c. {Step.FILE.value}, then {Step.NIP_CUTICLES.value}, then "
            f"{Step.BUFF.value}, then {Step.POLISH.value}. Never nip the "
            f"cuticles of a client with {DIABETES}.",
            "3. Finish service.",
        )),
        RuleSection("Stars and pay", (
            "If every step is right and in order, the client gives you a star "
            "and pays the full price.",
            "Any missing, extra, or out-of-order step means no star and $0.",
        )),
        RuleSection("Your goal", (
            f"Earn at least ${DAILY_GOAL} by the end of the day.",
        )),
    ]


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


# --- A day in progress (used by the browser, R7) ----------------------------

class Game:
    """One work day being played: the clients, the current client's steps so
    far, and the results of finished services. No input or printing."""

    def __init__(self, rng: random.Random):
        self.clients = generate_day(rng)
        self.index = 0
        self.steps: list[Step] = []
        self.results: list[ServiceResult] = []

    @property
    def is_over(self) -> bool:
        return self.index >= len(self.clients)

    @property
    def current_client(self) -> Client | None:
        return None if self.is_over else self.clients[self.index]

    def _require_client(self) -> Client:
        if self.is_over:
            raise ValueError("the day is over")
        return self.clients[self.index]

    def take_step(self, step: Step) -> None:
        self._require_client()
        self.steps.append(step)

    def finish(self) -> ServiceResult:
        """R5: judge the current client and move on to the next one."""
        result = finish_service(self._require_client(), self.steps)
        self.results.append(result)
        self.steps = []
        self.index += 1
        return result

    def day_result(self) -> DayResult:
        """R6: the end-of-day totals for the services finished so far."""
        return end_of_day(self.results)
