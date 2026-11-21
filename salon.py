"""Game logic for Nail Salon Tycoon.

This module holds every rule of the game and never talks to the terminal:
no input() and no print(). All randomness comes from a random.Random that the
caller passes in, so a seeded Random always produces the same day.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from decimal import Decimal
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

# R13: nail shapes a manicure or combo client can ask for (hands only)
NAIL_SHAPES = ("square", "round", "stiletto", "almond")

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
    PICK_COLOR = "Pick polish color"  # R12, round 5
    POLISH = "Polish"


@dataclass(frozen=True)
class Pick:
    """A step taken together with a choice (round 5): the color picked off the
    polish wall (R12), or the shape the hands are filed into (R13)."""

    step: Step
    choice: str


# Everything the player does is a Move: a plain Step, or a Step with a choice.
Move = Step | Pick


def step_of(move: Move) -> Step:
    """The Step behind a move, with any choice left off."""
    return move.step if isinstance(move, Pick) else move


def move_label(move: Move) -> str:
    """How a move is shown to the player, e.g. "File (almond)"."""
    if isinstance(move, Pick):
        return f"{move.step.value} ({move.choice})"
    return move.value


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
    nail_shape: str | None = None  # R13: from NAIL_SHAPES; None for a pedicure


def _random_client(rng: random.Random, hour: int, kind: str) -> Client:
    service = rng.choice(SERVICES)
    has_product = rng.random() < PRODUCT_CHANCE
    condition = (
        rng.choice(HEALTH_CONDITIONS)
        if rng.random() < HEALTH_CONDITION_CHANCE
        else None
    )
    color = rng.choice(list(POLISH_COLORS))
    shape = rng.choice(NAIL_SHAPES) if service.is_hand_service else None  # R13
    return Client(hour, kind, service, has_product, condition, color, shape)


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


def required_steps(client: Client) -> list[Move]:
    """R2, R3, R4: the one correct sequence of steps for this client.

    Each area is washed just before it is worked on: hands with WASH_HANDS,
    feet with WASH_FEET (R3 as changed in round 3). Each area's cuticles are
    nipped after filing and before buffing (R10), except for a client with
    diabetes (R11). The hands are filed into the client's shape (R13). The
    client's color is picked right before the first Polish only (R12); in a
    combo the feet reuse the same bottle.
    """
    nip = [] if client.health_condition == DIABETES else [Step.NIP_CUTICLES]
    steps: list[Move] = [Step.ASK_HEALTH]
    for i, area in enumerate(client.service.areas):
        steps.append(Step.WASH_HANDS if area == HANDS else Step.WASH_FEET)
        if client.has_product:
            steps.append(Step.REMOVE_PRODUCT)
        file = Pick(Step.FILE, client.nail_shape) if area == HANDS else Step.FILE
        pick = [Pick(Step.PICK_COLOR, client.polish_color)] if i == 0 else []
        steps += [file, *nip, Step.BUFF, *pick, Step.POLISH]
    return steps


def choices_for(client: Client, steps_taken: list[Move], step: Step) -> tuple[str, ...]:
    """Round 5: what the player must choose from when taking this step now.

    Picking a color offers the whole polish wall (R12). Filing the hands
    offers the nail shapes (R13). Every other step, including filing the
    feet, asks for nothing, so this returns ().
    """
    if step is Step.PICK_COLOR:
        return tuple(POLISH_COLORS)
    if step is Step.FILE and working_area(client, steps_taken) == HANDS:
        return NAIL_SHAPES
    return ()


@dataclass(frozen=True)
class ServiceResult:
    client: Client
    satisfied: bool    # True only with no mistakes
    stars: Decimal     # 1, 0.5, or 0 (round 6)
    earned: Decimal    # exact dollars and cents (round 6, decision 0009)
    mistakes: int = 0  # 0, 1, or 2, where 2 means "two or more"


def _one_change_away(wanted: list[Move], taken: list[Move]) -> bool:
    """True if one change turns `taken` into `wanted`: one skipped step, one
    extra step, one wrong step, or one step moved to another place."""
    if len(taken) == len(wanted) - 1:  # one skipped step
        return any(wanted[:i] + wanted[i + 1:] == taken for i in range(len(wanted)))
    if len(taken) == len(wanted) + 1:  # one extra step
        return any(taken[:i] + taken[i + 1:] == wanted for i in range(len(taken)))
    if len(taken) != len(wanted):
        return False
    if sum(a != b for a, b in zip(wanted, taken)) == 1:  # one wrong step
        return True
    for i, move in enumerate(taken):  # one step moved, near or far
        rest = taken[:i] + taken[i + 1:]
        if any(rest[:j] + [move] + rest[j:] == wanted for j in range(len(taken))):
            return True
    return False


def count_mistakes(client: Client, steps_taken: list[Move]) -> int:
    """R5 (round 6): 0 if the steps are exactly right, 1 if one change would
    make them right, and 2 for "two or more" (see decision 0008)."""
    wanted, taken = required_steps(client), list(steps_taken)
    if taken == wanted:
        return 0
    return 1 if _one_change_away(wanted, taken) else 2


def finish_service(client: Client, steps_taken: list[Move]) -> ServiceResult:
    """R5: judge the player's steps. No mistakes: a star and the full price.
    Exactly one mistake (round 6): half a star and half the price.
    Two or more: no star and $0."""
    mistakes = count_mistakes(client, steps_taken)
    price = Decimal(client.service.price)
    if mistakes == 0:
        stars, earned = Decimal(1), price
    elif mistakes == 1:
        stars, earned = Decimal("0.5"), price / 2
    else:
        stars, earned = Decimal(0), Decimal(0)
    return ServiceResult(client, mistakes == 0, stars, earned, mistakes)


def money(amount: Decimal | int) -> str:
    """An amount as text, with cents only when there are cents: "$25",
    "$12.50" (round 6)."""
    amount = Decimal(amount)
    if amount == amount.to_integral_value():
        return f"${int(amount)}"
    return f"${amount:.2f}"


# --- What the nails look like (R8) ------------------------------------------

@dataclass(frozen=True)
class NailLook:
    """How one area's nails look right now, so the browser can draw them."""

    has_product: bool          # old polish still on
    filed: bool
    buffed: bool
    polish_color: str | None   # None until polished
    cuticles_nipped: bool = False  # R10: ragged cuticles until nipped
    shape: str | None = None       # R13: the shape the player filed, if any


def _area_index(client: Client, steps_taken: list[Move]) -> int:
    """Which area the next step works on. Each Polish finishes an area."""
    polishes = sum(1 for s in steps_taken if step_of(s) is Step.POLISH)
    return min(polishes, len(client.service.areas) - 1)


def working_area(client: Client, steps_taken: list[Move]) -> str:
    """R8: the area shown now: hands, or feet after the first Polish in a combo."""
    return client.service.areas[_area_index(client, steps_taken)]


def brush_color(client: Client, steps_taken: list[Move]) -> str:
    """R12: the color Polish paints now: the latest color the player picked
    off the wall, right or wrong, or the client's own color if none yet."""
    for move in reversed(steps_taken):
        if isinstance(move, Pick) and move.step is Step.PICK_COLOR:
            return move.choice
    return client.polish_color


def nail_looks(client: Client, steps_taken: list[Move]) -> dict[str, NailLook]:
    """R8: replay the player's steps and return each area's nail look.

    This shows what the player did, right or wrong; judging happens only in
    finish_service. Asking about health, washing, and picking a color do not
    change nails.
    """
    looks = {
        area: NailLook(client.has_product, False, False, None)
        for area in client.service.areas
    }
    done: list[Move] = []
    for move in steps_taken:
        step = step_of(move)
        area = working_area(client, done)
        look = looks[area]
        if step is Step.REMOVE_PRODUCT:
            look = replace(look, has_product=False)
        elif step is Step.FILE:
            shape = move.choice if isinstance(move, Pick) else None  # R13
            look = replace(look, filed=True, shape=shape)
        elif step is Step.NIP_CUTICLES:
            look = replace(look, cuticles_nipped=True)
        elif step is Step.BUFF:
            look = replace(look, buffed=True)
        elif step is Step.POLISH:
            look = replace(look, polish_color=brush_color(client, done))  # R12
        looks[area] = look
        done.append(move)
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
            f"{Step.BUFF.value}, then {Step.PICK_COLOR.value}, then "
            f"{Step.POLISH.value}. Never nip the cuticles of a client with "
            f"{DIABETES}.",
            f"   d. When you file the hands, file them into the shape the "
            f"client wants ({', '.join(NAIL_SHAPES[:-1])}, or "
            f"{NAIL_SHAPES[-1]}).",
            f"   e. {Step.PICK_COLOR.value}: take the client's color off the "
            "polish wall. In a combo, pick it once, before polishing the hands; "
            "the feet use the same bottle.",
            "3. Finish service.",
        )),
        RuleSection("Stars and pay", (
            "If every step is right and in order, the client gives you a star "
            "and pays the full price.",
            "With exactly one mistake (one missing, extra, wrong, or "
            "out-of-place step), you get half a star and half the price.",
            "Two or more mistakes mean no star and $0.",
        )),
        RuleSection("Your goal", (
            f"Earn at least ${DAILY_GOAL} by the end of the day.",
        )),
    ]


# --- End of the day ---------------------------------------------------------

@dataclass(frozen=True)
class DayResult:
    results: tuple[ServiceResult, ...]
    total: Decimal
    goal: int
    goal_met: bool


def end_of_day(results: list[ServiceResult], goal: int = DAILY_GOAL) -> DayResult:
    """R6: total the day's earnings and check them against the daily goal."""
    total = sum((r.earned for r in results), Decimal(0))
    return DayResult(tuple(results), total, goal, total >= goal)


# --- A day in progress (used by the browser, R7) ----------------------------

class Game:
    """One work day being played: the clients, the current client's steps so
    far, and the results of finished services. No input or printing."""

    def __init__(self, rng: random.Random):
        self.clients = generate_day(rng)
        self.index = 0
        self.steps: list[Move] = []
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

    def choices_for(self, step: Step) -> tuple[str, ...]:
        """Round 5: what the player must choose from to take this step now."""
        return choices_for(self._require_client(), self.steps, step)

    def take_step(self, step: Move, choice: str | None = None) -> None:
        """Record a step. A step that needs a choice right now (a color for
        Pick polish color, a shape for filing the hands) must be given one of
        the offered options; any other step must not be given a choice."""
        if isinstance(step, Pick):
            step, choice = step.step, step.choice
        options = self.choices_for(step)
        if options and choice not in options:
            raise ValueError(f"{step.value}: choose one of {', '.join(options)}")
        if not options and choice is not None:
            raise ValueError(f"{step.value} takes no choice right now")
        self.steps.append(Pick(step, choice) if options else step)

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
