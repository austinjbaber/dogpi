"""Idle mode renderer and controls."""

import random
import time

from PIL import Image, ImageDraw

from hardware import device, W, H

from .clock import ClockAnimator
from .icosahedron import IcosahedronBackground
from .rain_v2 import RainV2Background
from .starfield import StarfieldBackground
from .tesseract import TesseractBackground

# Idle render pacing target for SH1106 over I2C.
IDLE_TARGET_FPS = 40.0
IDLE_FRAME_TIME_S = 1.0 / IDLE_TARGET_FPS

_rng = random.Random()

_clock = ClockAnimator(
    width=W,
    height=H,
    rng=_rng,
    font_paths=[
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf",
    ],
)

_backgrounds = [
    ("rain", RainV2Background(width=W, height=H, rng=_rng)),
    ("icosahedron", IcosahedronBackground(width=W, height=H, rng=_rng)),
    ("starfield", StarfieldBackground(width=W, height=H, rng=_rng)),
    ("tesseract", TesseractBackground(width=W, height=H, rng=_rng)),
]

# Track the active background and frame timing for animation
_bg_index = 0
_last_t = time.monotonic()


def _cycle_background():
    global _bg_index
    _bg_index = (_bg_index + 1) % len(_backgrounds)


def _cycle_font():
    _clock.cycle_font()


def render_idle_frame():
    global _last_t

    now_m = time.monotonic()
    dt = now_m - _last_t
    _last_t = now_m

    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    time_str = _clock.prepare(draw)

    bg_name, background = _backgrounds[_bg_index]
    if bg_name == "starfield":
        # For starfield, move the clock first so stars can avoid its center area. (starfield looks way better when clock doesn't cover the edge)
        _clock.update_position(dt, use_starfield_buffer=True)
        background.update_and_draw(
            draw,
            dt,
            _clock.tx + (_clock.box_w / 2.0),
            _clock.ty + (_clock.box_h / 2.0),
        )
        _clock.draw(draw, time_str)
    else:
        # Other backgrounds do not need clock-position awareness.
        background.update_and_draw(draw, dt)
        _clock.update_position(dt, use_starfield_buffer=False)
        _clock.draw(draw, time_str)

    device.display(img)

    # Cap idle rendering to reduce I2C bus pressure and keep timing predictable.
    elapsed = time.monotonic() - now_m
    remaining = IDLE_FRAME_TIME_S - elapsed
    if remaining > 0:
        time.sleep(remaining)
