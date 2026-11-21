"""Terminal front end for Nail Salon Tycoon.

Only menus, prompts, and printing live here. Every rule of the game is in
salon.py. Run with:  python3 game.py   (optionally --seed N)
"""

from __future__ import annotations

import argparse
import random

import salon

MENU = list(salon.Step)  # numbered 1..9 in this order
FINISH = len(MENU) + 1


def format_hour(hour: int) -> str:
    return f"{hour:02d}:00"


def describe_client(client: salon.Client) -> str:
    nails = "has old polish on" if client.has_product else "has bare nails"
    wants = f"Wants {client.polish_color} polish"  # R12
    if client.nail_shape:  # R13: hand services only
        wants += f" and {client.nail_shape} nails"
    return (
        f"{format_hour(client.hour)}  {client.kind.upper()}: "
        f"{client.service.name} ({salon.money(client.service.price)}), client {nails}. "
        f"{wants}."
    )


def ask_choice() -> int:
    """Keep asking until the player types a valid menu number."""
    while True:
        raw = input("Choose a step: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= FINISH:
            return int(raw)
        print(f"  Please type a number from 1 to {FINISH}.")


def ask_option(question: str, options: tuple[str, ...]) -> str:
    """Round 5: show numbered options and keep asking until one is chosen."""
    print(f"  {question}")
    for number, option in enumerate(options, start=1):
        print(f"    {number}. {option}")
    while True:
        raw = input("  Your choice: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  Please type a number from 1 to {len(options)}.")


QUESTIONS = {  # round 5: what to ask when a step needs a choice
    salon.Step.PICK_COLOR: "Which color do you take off the polish wall?",
    salon.Step.FILE: "Which shape do you file?",
}


def run_service(client: salon.Client) -> salon.ServiceResult:
    print()
    print("-" * 60)
    print(describe_client(client))
    if len(client.service.areas) > 1:
        print("Work on the hands first, then the feet.")
    steps: list[salon.Move] = []
    while True:
        print()
        for number, step in enumerate(MENU, start=1):
            print(f"  {number}. {step.value}")
        print(f"  {FINISH}. Finish service")
        if steps:
            print("Steps so far: " + ", ".join(salon.move_label(s) for s in steps))
        choice = ask_choice()
        if choice == FINISH:
            break
        step = MENU[choice - 1]
        options = salon.choices_for(client, steps, step)
        picked = ask_option(QUESTIONS[step], options) if options else None
        steps.append(salon.Pick(step, picked) if picked else step)
        if step is salon.Step.PICK_COLOR:
            print(f"  You take the {picked} bottle off the polish wall.")
        elif step is salon.Step.FILE and picked:
            article = "an" if picked[0] in "aeiou" else "a"
            print(f"  You file the nails into {article} {picked} shape.")
        elif step is salon.Step.ASK_HEALTH:
            print(f"  Client: {salon.health_answer(client)}")
        elif step is salon.Step.WASH_HANDS:
            print("  The client washes their hands.")
        elif step is salon.Step.WASH_FEET:
            print("  The client's feet soak in the warm foot bath.")
        elif step is salon.Step.NIP_CUTICLES:
            print("  You carefully nip the cuticles.")
        else:
            print(f"  You {step.value.lower()}.")

    result = salon.finish_service(client, steps)
    if result.satisfied:
        print(f"\nThe client is satisfied and gives you a star! "
              f"+{salon.money(result.earned)}")
    else:
        if result.mistakes == 1:  # round 6 (R5)
            print("\nThe client is partly satisfied: one step was wrong. "
                  f"Half a star! +{salon.money(result.earned)}")
        else:
            print("\nThe client is not satisfied. No star, no payment.")
        expected = ", ".join(salon.move_label(s) for s in salon.required_steps(client))
        print(f"  The correct steps were: {expected}")
    return result


# How a result's star is shown, by number of mistakes: a full star, half a
# star, or none (round 6).
STAR_MARKS = {0: "★", 1: "½", 2: "–"}


def print_summary(day: salon.DayResult) -> None:
    print()
    print("=" * 60)
    print("END OF DAY")
    for r in day.results:
        star = STAR_MARKS[r.mistakes]
        print(
            f"  {format_hour(r.client.hour)}  {r.client.kind:<11} "
            f"{r.client.service.name:<18} {star}  {salon.money(r.earned)}"
        )
    print(f"Total earnings: {salon.money(day.total)}")
    if day.goal_met:
        print(f"Daily goal of {salon.money(day.goal)} met. Great work!")
    else:
        print(f"Daily goal of {salon.money(day.goal)} not met. Try again tomorrow.")


def print_rules() -> None:
    """R9: show the rules (written in salon.py) before the day begins."""
    print("=" * 60)
    print("RULES")
    for section in salon.rules():
        print()
        print(section.heading)
        for line in section.lines:
            print(f"  {line}")
    print("=" * 60)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Nail Salon Tycoon")
    parser.add_argument("--seed", type=int, help="replay the same day")
    args = parser.parse_args(argv)

    print("Welcome to your first day at the salon!")
    print_rules()
    try:
        input("Press Enter to begin the day... ")
    except (EOFError, KeyboardInterrupt):
        print("\nYou left the salon early. Goodbye!")
        return

    rng = random.Random(args.seed)
    clients = salon.generate_day(rng)
    print(f"You have {len(clients)} clients today. Goal: {salon.money(salon.DAILY_GOAL)}.")
    try:
        results = [run_service(c) for c in clients]
    except (EOFError, KeyboardInterrupt):
        print("\nYou left the salon early. Goodbye!")
        return
    print_summary(salon.end_of_day(results))


if __name__ == "__main__":
    main()
