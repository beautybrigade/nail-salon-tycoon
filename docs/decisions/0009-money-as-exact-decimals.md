# 0009: Keep money as exact decimals with Python's Decimal (R5, R6, round 6)

Status: accepted (round 6)

In the context of **half pay for one mistake (R5, round 6), where the
student chose to keep the cents ($12.50, $17.50, $27.50) and the day's
total is compared with the $150 goal (R6)**, facing **prices and totals
that were whole-dollar `int`s in `salon.py`, a terminal and a browser page
that both write amounts, and more than 20 earlier tests that compare
amounts with whole numbers such as `25` and `150`**, we decided for
**`decimal.Decimal` for `ServiceResult.stars`, `ServiceResult.earned` and
`DayResult.total`, leaving prices and the goal as whole-dollar `int`s,
with `salon.money()` to write an amount as "$25" or "$12.50" and
`web.number()` to send it to the page as a JSON number (25 or 12.5)**, and
neglected **floats, whole cents stored as `int`s (2500 for $25), and
`fractions.Fraction`**, to achieve **exact amounts that never show up as
$27.499999, totals that compare exactly with the goal, earlier tests that
still pass because `Decimal(25) == 25` is true, and one place in Python
that decides how an amount is written**, accepting that **`web.py` has to
convert `Decimal`s before turning them into JSON (the `json` module can't
handle them), the page has a small `money()` function of its own to write
the numbers it receives, and anyone adding new amounts must use `Decimal`,
not `float`.**

## Why the alternatives were not chosen

- **Floats.** Halves happen to be exact in a float, but floats are a
  well-known source of money bugs (`0.1 + 0.2 != 0.3`). If a later round
  adds tips or a percentage, wrong totals could appear without any warning.
- **Whole cents as `int`s.** This is exact and common in real shops, but
  every price, the goal, the rules text, and many earlier tests would
  change from 25 to 2500, and every place that shows an amount would need
  to divide by 100.
- **`Fraction`.** This is exact too, but it shows up as `55/2`, which is
  harder to read, and it is less familiar for money than `Decimal`.
