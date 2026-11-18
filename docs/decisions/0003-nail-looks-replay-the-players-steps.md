# 0003: Work out the nail look by replaying the player's steps

Status: accepted (round 2)

In the context of **showing the nails change as the player works (R8), while
mistakes are still judged only at Finish service (student's choice; see
decision 0001)**, facing **the need to draw something sensible even when the
player picks steps in the wrong order, and to know whether a combo's step
applies to the hands or the feet**, we decided for **`salon.nail_looks`, which
replays the steps taken so far and applies each one to the current area (each
Polish finishes an area, so a combo moves from hands to feet after the first
Polish), showing exactly what the player did, right or wrong**, and neglected
**drawing the nails from how far the player's steps match the correct sequence
(the nails would freeze at the first mistake and give the answer away), a
"switch to feet" button (a new step that is not in the requirements), and
letting the page track the look by itself in JavaScript (a second copy of the
rules, against decision 0002)**, to achieve **nails that always react to the
step just picked, no hint about mistakes before Finish, and a look that is
easy to test with pytest**, accepting that **a player who never polishes the
hands in a combo will never see the feet, and some wrong sequences produce odd
looks (for example polish over old product shows just the new color).**
