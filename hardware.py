"""Hardware setup — buttons, OLED display, and fonts."""

from gpiozero import Button
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import ImageFont

I2C_ADDR = 0x3C

# ----------------------------
# Buttons
# ----------------------------
BTN_UP   = Button(17, pull_up=True, bounce_time=0.12)
BTN_SEL  = Button(27, pull_up=True, bounce_time=0.12)
BTN_DOWN = Button(22, pull_up=True, bounce_time=0.12)

# ----------------------------
# OLED
# ----------------------------
serial = i2c(port=1, address=I2C_ADDR)
device = sh1106(serial)
W, H = device.size

# ----------------------------
# Fonts
# ----------------------------
def try_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return None

SCREEN_FONT = (
    try_font("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 12)
    or ImageFont.load_default()
)

TOAST_FONT = (
    try_font("/usr/share/fonts/truetype/freeFont/FreeMono.ttf", 12)
    or SCREEN_FONT
)

WHEN_FONT = (
    try_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
    or SCREEN_FONT
)
