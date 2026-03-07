"""Idle screen — rain animation with a DVD-bounce clock."""

from importlib.resources import path
import random
import time
from datetime import datetime
from helpers import get_12_hour_clock_time
from PIL import Image, ImageDraw, ImageFont

from hardware import device, W, H

# ----------------------------
# Layout constants
# ----------------------------
IDLE_PAD    = 3
IDLE_BORDER = 2

# ----------------------------
# Rain
# ----------------------------
NUM_DROPS = 40
DROP_LEN_MIN, DROP_LEN_MAX = 3, 10
DROP_SPD_MIN, DROP_SPD_MAX = 0.8, 3.0

rng = random.Random()

drops = [{
    "x":   rng.randrange(0, W),
    "y":   rng.uniform(-H, 0),
    "len": rng.randint(DROP_LEN_MIN, DROP_LEN_MAX),
    "spd": rng.uniform(DROP_SPD_MIN, DROP_SPD_MAX),
} for _ in range(NUM_DROPS)]

# ----------------------------
# DVD bounce
# ----------------------------
MIN_SPD, MAX_SPD = 0.5, 1.5

def _rand_speed():
    return rng.uniform(MIN_SPD, MAX_SPD)

_tx, _ty = 0.0, 0.0
_vx, _vy = _rand_speed(), _rand_speed()

_last_t        = time.monotonic()
_last_time_str = None
_idle_font     = None
_tbx0 = _tby0  = 0
_tw   = _th     = 0

# font cycling globals
_font_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf",
]
_font_index = 0


def _load_font():
    """Return the currently selected font.

    The index is advanced by pressing the DOWN button (hardware.BTN_DOWN).
    """
    try:
        return ImageFont.truetype(_font_paths[_font_index], 20)
    except Exception:
        return ImageFont.load_default()


def _cycle_font():
    """Move to the next font in the list and force a reload of the time string.

    This function is bound to ``BTN_DOWN.when_pressed`` during module import so
    that the user can press the hardware button to change the font while the
    idle animation is running.
    """
    global _font_index, _last_time_str
    _font_index = (_font_index + 1) % len(_font_paths)
    # reset last time to trigger a size recalculation on next frame
    _last_time_str = None

def render_idle_frame():
    global _last_t, _tx, _ty, _vx, _vy
    global _last_time_str, _idle_font, _tbx0, _tby0, _tw, _th
    global _font_index

    now_m = time.monotonic()
    dt = now_m - _last_t
    _last_t = now_m

    step = dt * 40.0

    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    # --- Rain ---
    for d in drops:
        d["y"] += d["spd"] * step
        if d["y"] - d["len"] > H:
            d["x"]   = rng.randrange(0, W)
            d["y"]   = rng.uniform(-10, 0)
            d["len"] = rng.randint(DROP_LEN_MIN, DROP_LEN_MAX)
            d["spd"] = rng.uniform(DROP_SPD_MIN, DROP_SPD_MAX)

        x  = int(d["x"])
        y0 = int(d["y"] - d["len"])
        y1 = int(d["y"])
        draw.line((x, y0, x, y1), fill=255)

    # --- Time string ---
    time_str = get_12_hour_clock_time(datetime.now().time())

    if time_str != _last_time_str:
        _last_time_str = time_str
        _idle_font = _load_font()

        _tbx0, _tby0, tbx1, tby1 = draw.textbbox((0, 0), time_str, font=_idle_font)
        _tw, _th = (tbx1 - _tbx0), (tby1 - _tby0)

    box_w = _tw + 2 * (IDLE_PAD + IDLE_BORDER)
    box_h = _th + 2 * (IDLE_PAD + IDLE_BORDER)

    # --- Bounce ---
    _tx += _vx * step
    _ty += _vy * step

    hit_x = False
    hit_y = False

    if _tx <= 0:
        _tx = 0;          hit_x = True
    if _tx + box_w >= W:
        _tx = W - box_w;  hit_x = True
    if _ty <= 0:
        _ty = 0;          hit_y = True
    if _ty + box_h >= H:
        _ty = H - box_h;  hit_y = True

    if hit_x:
        _vx = -_vx
        _vx = (1 if _vx > 0 else -1) * _rand_speed()
    if hit_y:
        _vy = -_vy
        _vy = (1 if _vy > 0 else -1) * _rand_speed()

    ix, iy = int(_tx), int(_ty)

    # --- Box border ---
    draw.rectangle((ix, iy, ix + box_w - 1, iy + box_h - 1), fill=0)
    for i in range(IDLE_BORDER):
        draw.rectangle(
            (ix + i, iy + i, ix + box_w - 1 - i, iy + box_h - 1 - i),
            outline=255,
        )

    # --- Center the text ---
    inner_x = ix + IDLE_BORDER + IDLE_PAD
    inner_y = iy + IDLE_BORDER + IDLE_PAD
    inner_w = box_w - 2 * (IDLE_BORDER + IDLE_PAD)
    inner_h = box_h - 2 * (IDLE_BORDER + IDLE_PAD)

    text_x = inner_x + (inner_w - _tw) // 2 - _tbx0
    text_y = inner_y + (inner_h - _th) // 2 - _tby0

    draw.text((text_x, text_y), time_str, font=_idle_font, fill=255)

    device.display(img)
