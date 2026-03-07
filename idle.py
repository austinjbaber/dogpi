"""Idle screen — rain animation with a DVD-bounce clock."""

from importlib.resources import path
import math
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

def _draw_rain(draw, step):
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

# ----------------------------
# Icosahedron background
# ----------------------------
_phi = (1.0 + math.sqrt(5.0)) / 2.0

_ICO_VERTS = [
    (-1,  _phi, 0), ( 1,  _phi, 0), (-1, -_phi, 0), ( 1, -_phi, 0),
    (0, -1,  _phi), (0,  1,  _phi), (0, -1, -_phi), (0,  1, -_phi),
    ( _phi, 0, -1), ( _phi, 0,  1), (-_phi, 0, -1), (-_phi, 0,  1),
]

_ICO_EDGES = [
    (0,11),(0,5),(0,1),(0,7),(0,10),
    (1,5),(1,9),(1,8),(1,7),
    (2,3),(2,4),(2,6),(2,10),(2,11),
    (3,4),(3,9),(3,8),(3,6),
    (4,5),(4,9),(4,11),
    (5,9),(5,11),
    (6,7),(6,8),(6,10),
    (7,8),(7,10),
    (8,9),
    (10,11),
]

_max_r = max(math.sqrt(x*x+y*y+z*z) for x,y,z in _ICO_VERTS)
_ICO_VERTS = [(x/_max_r, y/_max_r, z/_max_r) for x,y,z in _ICO_VERTS]

_ICO_CAMERA_Z  = 4.0
_ICO_SCALE     = 18.0
_ICO_MARGIN    = 12
_ICO_ROT_X_SPD = 0.45
_ICO_ROT_Y_SPD = 0.70
_ICO_ROT_Z_SPD = 0.25

_ico_ax = _ico_ay = _ico_az = 0.0
_ico_cx, _ico_cy = W / 2.0, H / 2.0
_ico_vx = rng.uniform(6, 12) * rng.choice((-1, 1))
_ico_vy = rng.uniform(4, 8)  * rng.choice((-1, 1))

def _ico_rotate(verts, ax, ay, az):
    sx, cx = math.sin(ax), math.cos(ax)
    sy, cy = math.sin(ay), math.cos(ay)
    sz, cz = math.sin(az), math.cos(az)
    out = []
    for x, y, z in verts:
        y, z = y*cx - z*sx, y*sx + z*cx
        x, z = x*cy + z*sy, -x*sy + z*cy
        x, y = x*cz - y*sz, x*sz + y*cz
        out.append((x, y, z))
    return out

def _ico_project(verts, cx, cy):
    pts = []
    for x, y, z in verts:
        f = _ICO_CAMERA_Z / (_ICO_CAMERA_Z + z)
        px = int(cx + x * _ICO_SCALE * f)
        py = int(cy + y * _ICO_SCALE * f)
        pts.append((px, py))
    return pts

def _draw_icosahedron(draw, step):
    global _ico_ax, _ico_ay, _ico_az, _ico_cx, _ico_cy, _ico_vx, _ico_vy

    dt = step / 40.0

    _ico_ax += _ICO_ROT_X_SPD * dt
    _ico_ay += _ICO_ROT_Y_SPD * dt
    _ico_az += _ICO_ROT_Z_SPD * dt

    _ico_cx += _ico_vx * dt
    _ico_cy += _ico_vy * dt
    if _ico_cx < _ICO_MARGIN:
        _ico_cx = _ICO_MARGIN; _ico_vx = abs(_ico_vx)
    if _ico_cx > W - _ICO_MARGIN:
        _ico_cx = W - _ICO_MARGIN; _ico_vx = -abs(_ico_vx)
    if _ico_cy < _ICO_MARGIN:
        _ico_cy = _ICO_MARGIN; _ico_vy = abs(_ico_vy)
    if _ico_cy > H - _ICO_MARGIN:
        _ico_cy = H - _ICO_MARGIN; _ico_vy = -abs(_ico_vy)

    rotated   = _ico_rotate(_ICO_VERTS, _ico_ax, _ico_ay, _ico_az)
    projected = _ico_project(rotated, _ico_cx, _ico_cy)

    for a, b in _ICO_EDGES:
        draw.line((projected[a], projected[b]), fill=255)
    for px, py in projected:
        if 0 <= px < W and 0 <= py < H:
            draw.point((px, py), fill=255)

# ----------------------------
# Background cycling
# ----------------------------
_backgrounds = [_draw_rain, _draw_icosahedron]
_bg_index = 0

def _cycle_background():
    global _bg_index
    _bg_index = (_bg_index + 1) % len(_backgrounds)

# ----------------------------
# DVD bounce
# ----------------------------
MIN_SPD, MAX_SPD = 0.5, 1.2

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
    """Return the currently selected font
    The index is cycled by pressing the DOWN button
    """
    try:
        return ImageFont.truetype(_font_paths[_font_index], 20)
    except Exception:
        return ImageFont.load_default()


def _cycle_font():
    """Move to the next font in the list   """
    global _font_index, _last_time_str
    _font_index = (_font_index + 1) % len(_font_paths)
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

    # --- Background ---
    _backgrounds[_bg_index](draw, step)

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