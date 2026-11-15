"""Terminal front end for Nail Salon Tycoon.

Only menus, prompts, and printing live here. Every rule of the game is in
salon.py. Run with:  python3 game.py   (optionally --seed N)
"""

from __future__ import annotations

import argparse
import random

import salon

MENU = list(salon.Step)  # numbered 1..6 in this order
FINISH = len(MENU) + 1


def format_hour(hour: int) -> str:
    return f"{hour:02d}:00"


def describe_client(client: salon.Client) -> str:
    nails = "has old polish on" if client.has_product else "has bare nails"
    return (
        f"{format_hour(client.hour)}  {client.kind.upper()}: "
        f"{client.service.name} (${client.service.price}), client {nails}."
    )


def ask_choice() -> int:
    """Keep asking until the player types a valid menu number."""
    while True:
        raw = input("Choose a step: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= FINISH:
            return int(raw)
        print(f"  Please type a number from 1 to {FINISH}.")


def run_service(client: salon.Client) -> salon.ServiceResult:
    print()
    print("-" * 60)
    print(describe_client(client))
    if len(client.service.areas) > 1:
        print("Work on the hands first, then the feet.")
    steps: list[salon.Step] = []
    while True:
        print()
        for number, step in enumerate(MENU, start=1):
            print(f"  {number}. {step.value}")
        print(f"  {FINISH}. Finish service")
        if steps:
            print("Steps so far: " + ", ".join(s.value for s in steps))
        choice = ask_choice()
        if choice == FINISH:
            break
        step = MENU[choice - 1]
        steps.append(step)
        if step is salon.Step.ASK_HEALTH:
            print(f"  Client: {salon.health_answer(client)}")
        elif step is salon.Step.WASH_HANDS:
            print("  The client washes their hands.")
        else:
            print(f"  You {step.value.lower()}.")

    result = salon.finish_service(client, steps)
    if result.satisfied:
        print(f"\nThe client is satisfied and gives you a star! +${result.earned}")
    else:
        print("\nThe client is not satisfied. No star, no payment.")
        expected = ", ".join(s.value for s in salon.required_steps(client))
        print(f"  The correct steps were: {expected}")
    return result


def print_summary(day: salon.DayResult) -> None:
    print()
    print("=" * 60)
    print("END OF DAY")
    for r in day.results:
        star = "*" if r.stars else "-"
        print(
            f"  {format_hour(r.client.hour)}  {r.client.kind:<11} "
            f"{r.client.service.name:<18} {star}  ${r.earned}"
        )
    print(f"Total earnings: ${day.total}")
    if day.goal_met:
        print(f"Daily goal of ${day.goal} met. Great work!")
    else:
        print(f"Daily goal of ${day.goal} not met. Try again tomorrow.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Nail Salon Tycoon")
    parser.add_argument("--seed", type=int, help="replay the same day")
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    clients = salon.generate_day(rng)
    print("Welcome to your first day at the salon!")
    print(f"You have {len(clients)} clients today. Goal: ${salon.DAILY_GOAL}.")

    try:
        results = [run_service(c) for c in clients]
    except (EOFError, KeyboardInterrupt):
        print("\nYou left the salon early. Goodbye!")
        return
    print_summary(salon.end_of_day(results))


if __name__ == "__main__":
    main()
