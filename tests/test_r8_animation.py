"""R8: animated, technician's point of view, one animation per step, nails
change as the player works, lots of color."""

import random
import re
from pathlib import Path

import salon
import web
from helpers import make_client

S = salon.Step
STATIC = Path(__file__).resolve().parent.parent / "static"


# --- Each step has its own animation --------------------------------------

def test_r8_every_step_has_its_own_animation():
    assert set(web.STEP_ANIMATIONS) == set(S)
    names = list(web.STEP_ANIMATIONS.values())
    assert len(set(names)) == len(names), "two steps share an animation"


def test_r8_page_script_plays_each_step_animation():
    script = (STATIC / "app.js").read_text()
    for name in web.STEP_ANIMATIONS.values():
        assert f'"{name}"' in script, f"app.js has no animation for {name}"


def test_r8_stylesheet_has_keyframes_for_each_step_animation():
    css = (STATIC / "style.css").read_text()
    for name in web.STEP_ANIMATIONS.values():
        assert f"@keyframes {name}" in css, f"style.css has no @keyframes {name}"


def test_r8_page_draws_hands_and_feet_from_technician_view():
    page = (STATIC / "index.html").read_text()
    assert 'id="hand-view"' in page
    assert 'id="foot-view"' in page


# --- The nails change as the player works ----------------------------------

def test_r8_nails_start_with_old_product_until_removed():
    client = make_client(salon.MANICURE, has_product=True)
    assert salon.nail_looks(client, [])[salon.HANDS].has_product
    after = salon.nail_looks(client, [S.ASK_HEALTH, S.WASH_HANDS, S.REMOVE_PRODUCT])
    assert not after[salon.HANDS].has_product


def test_r8_bare_nails_start_plain():
    look = salon.nail_looks(make_client(salon.PEDICURE), [])[salon.FEET]
    assert look == salon.NailLook(has_product=False, filed=False,
                                  buffed=False, polish_color=None)


def test_r8_file_buff_polish_each_change_the_nails():
    client = make_client(salon.PEDICURE, color="Hot Pink")
    steps = [S.ASK_HEALTH]
    seen = []
    for step in (S.FILE, S.BUFF, S.POLISH):
        steps.append(step)
        seen.append(salon.nail_looks(client, steps)[salon.FEET])
    filed, buffed, polished = seen
    assert filed.filed and not filed.buffed and filed.polish_color is None
    assert buffed.buffed and buffed.polish_color is None
    assert polished.polish_color == "Hot Pink"


def test_r8_nails_look_polished_after_polish_step():
    client = make_client(salon.MANICURE, color="Electric Blue")
    look = salon.nail_looks(client, salon.required_steps(client))[salon.HANDS]
    assert look == salon.NailLook(has_product=False, filed=True,
                                  buffed=True, polish_color="Electric Blue",
                                  cuticles_nipped=True,  # R10 (round 4)
                                  shape="almond")        # R13 (round 5)


def test_r8_talking_and_washing_do_not_change_the_nails():
    client = make_client(salon.MANICURE, has_product=True)
    assert (salon.nail_looks(client, [S.ASK_HEALTH, S.WASH_HANDS])
            == salon.nail_looks(client, []))


def test_r8_wrong_order_still_shows_what_the_player_did():
    client = make_client(salon.MANICURE, color="Sunny Yellow")
    look = salon.nail_looks(client, [S.POLISH])[salon.HANDS]
    assert look.polish_color == "Sunny Yellow"
    assert not look.filed


def test_r8_combo_works_on_hands_then_feet_after_first_polish():
    client = make_client(salon.COMBO, has_product=True, color="Lime Green")
    hands_done = [S.ASK_HEALTH, S.WASH_HANDS, S.REMOVE_PRODUCT,
                  S.FILE, S.BUFF, S.POLISH]
    assert salon.working_area(client, hands_done[:-1]) == salon.HANDS
    assert salon.working_area(client, hands_done) == salon.FEET
    looks = salon.nail_looks(client, hands_done + [S.REMOVE_PRODUCT, S.FILE])
    assert looks[salon.HANDS].polish_color == "Lime Green"
    assert looks[salon.FEET] == salon.NailLook(has_product=False, filed=True,
                                               buffed=False, polish_color=None)


def test_r8_single_area_service_never_switches_area():
    client = make_client(salon.MANICURE)
    steps = [S.POLISH, S.POLISH, S.FILE]
    assert salon.working_area(client, steps) == salon.HANDS
    assert set(salon.nail_looks(client, steps)) == {salon.HANDS}


# --- Lots of color ----------------------------------------------------------

def test_r8_palette_has_many_bright_colors():
    assert len(salon.POLISH_COLORS) >= 6
    for name, hex_code in salon.POLISH_COLORS.items():
        assert re.fullmatch(r"#[0-9a-fA-F]{6}", hex_code), name


def test_r8_each_client_requests_a_color_from_the_palette():
    colors = set()
    for seed in range(30):
        for client in salon.generate_day(random.Random(seed)):
            assert client.polish_color in salon.POLISH_COLORS
            colors.add(client.polish_color)
    assert len(colors) > 1, "every client asked for the same color"


def test_r8_same_seed_gives_same_colors():
    first = [c.polish_color for c in salon.generate_day(random.Random(5))]
    again = [c.polish_color for c in salon.generate_day(random.Random(5))]
    assert first == again
