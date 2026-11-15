# Nail Salon Tycoon — standing rules

These rules apply to every session in this project.

1. **Requirements belong to the student.** The requirements in `problem.md` are
   written by the student. The assistant must not change `problem.md`. If a
   requirement looks wrong or unclear, ask the student. Record clarified
   decisions in `spec.md`.
2. **Logic stays separate from terminal I/O.** All game logic lives in
   `salon.py`, which must never call `input()` or `print()`. `game.py` holds
   only the terminal part (menus, prompts, printing) and calls `salon.py`.
   Randomness in `salon.py` comes from a `random.Random` that is passed in, so
   tests can use a seed.
3. **Every test names its requirement.** Each test's name or docstring names
   the requirement ID it checks (for example `R4`). A test must fail if the
   code it checks is wrong.
4. **Standard library only.** No third-party packages, no virtual
   environments, no API keys, logins, or paid services. pytest is the only
   extra tool. Run the tests with `python3 -m pytest`.
5. **Never undo or amend a commit.** No `git commit --amend`, `git reset`,
   `git revert` of the student's work, rebases, or force pushes. Fix mistakes
   with a new commit. Do not push; the student pushes.
