"""Idle mode renderer and controls."""

import random
import time

from PIL import Image, ImageDraw

from hardware import device, W, H

from .clock import ClockAnimator
from .icosahedron import IcosahedronBackground
from .rain import RainBackground
from .starfield import StarfieldBackground
from .tesseract import TesseractBackground

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
    ("rain", RainBackground(width=W, height=H, rng=_rng)),
    ("icosahedron", IcosahedronBackground(width=W, height=H, rng=_rng)),
    ("starfield", StarfieldBackground(width=W, height=H, rng=_rng)),
    ("tesseract", TesseractBackground(width=W, height=H, rng=_rng)),
]
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
    step = dt * 40.0

    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    time_str = _clock.prepare(draw)

    bg_name, background = _backgrounds[_bg_index]
    if bg_name == "starfield":
        _clock.update_position(step, use_starfield_buffer=True)
        background.update_and_draw(
            draw,
            step,
            _clock.tx + (_clock.box_w / 2.0),
            _clock.ty + (_clock.box_h / 2.0),
        )
        _clock.draw(draw, time_str)
    else:
        background.update_and_draw(draw, step)
        _clock.update_position(step, use_starfield_buffer=False)
        _clock.draw(draw, time_str)

    device.display(img)
