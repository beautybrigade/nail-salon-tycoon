# 0001: Judge a service by comparing to one exact step sequence

Status: accepted (round 1)

In the context of **judging whether a client is satisfied (R4, R5)**, facing
**the need for a rule that is easy to explain to a beginner, easy to test, and
strict about step order**, we decided for **building the one correct list of
steps for each client (`required_steps`) and requiring the player's steps to
match it exactly**, and neglected **a points system that takes off a little for
each mistake, a set of separate rule checks (for example "file comes before
buff", "health is asked first"), and stopping the player the moment they pick a
wrong step**, to achieve **a single rule that covers every mistake listed in
spec.md (skipped, extra, repeated, or out-of-order steps), and a correct answer
that the game can show the player after a failed service**, accepting that
**every mistake counts the same (a forgotten hand wash costs as much as a
forgotten polish), and the player gets no partial credit or explanation of
which step was wrong.**
