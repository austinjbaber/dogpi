"""Input handling — button callbacks and wiring."""

import time

from hardware import BTN_UP, BTN_DOWN, BTN_SEL, device, SCREEN_FONT
from idle import _cycle_font, _cycle_background
from screens import (
    ui,
    MODE_IDLE, MODE_STATUS, MODE_MENU, MODE_WHEN, MODE_WEATHER, MODE_FORECAST,
    menu, MINUTES_OPTIONS, MAX_WHEN_HOURS,
    do_menu_action, commit_pending_log, show_toast, weather_lines, forecast_lines,
)


def _note_input():
    """Reset the inactivity timer for any button interaction."""
    ui.last_input_t = time.monotonic()


def _scroll_offset(lines, current_offset, delta):
    """Clamp a scroll offset to the visible line window for the current font."""
    bbox = SCREEN_FONT.getbbox("Ag") # use a typical character to get line height
    font_h = bbox[3] - bbox[1]
    line_h = font_h + 1
    max_lines = device.height // line_h
    max_scroll = max(0, len(lines) - max_lines)
    return max(0, min(current_offset + delta, max_scroll))


def _menu_index_for(action_type):
    """Return the menu index for an action type, defaulting to the first item."""
    return next((i for i, (_, action) in enumerate(menu) if action.get("type") == action_type), 0)


def on_up():
    _note_input()

    if ui.mode == MODE_IDLE:
        _cycle_background()
        return

    if ui.mode == MODE_MENU: # scroll up
        ui.menu_idx = (ui.menu_idx - 1) % len(menu)

    elif ui.mode == MODE_WHEN:
        if ui.when_field == "hours":
            ui.when_hours = (ui.when_hours + 1) % (MAX_WHEN_HOURS + 1)
        else:
            ui.when_min_idx = (ui.when_min_idx + 1) % len(MINUTES_OPTIONS)

    elif ui.mode == MODE_WEATHER:
        ui.weather_scroll = _scroll_offset(weather_lines(), ui.weather_scroll, -1) # scroll up

    elif ui.mode == MODE_FORECAST:
        ui.forecast_scroll = _scroll_offset(forecast_lines(), ui.forecast_scroll, -1) # scroll up


def on_down():
    _note_input()

    if ui.mode == MODE_IDLE:
        _cycle_font()
        return

    if ui.mode == MODE_MENU: # scroll down
        ui.menu_idx = (ui.menu_idx + 1) % len(menu)

    elif ui.mode == MODE_WHEN:
        if ui.when_field == "hours":
            ui.when_hours = (ui.when_hours - 1) % (MAX_WHEN_HOURS + 1)
        else:
            ui.when_min_idx = (ui.when_min_idx - 1) % len(MINUTES_OPTIONS)

    elif ui.mode == MODE_WEATHER:
        ui.weather_scroll = _scroll_offset(weather_lines(), ui.weather_scroll, 1) # scroll down

    elif ui.mode == MODE_FORECAST:
        ui.forecast_scroll = _scroll_offset(forecast_lines(), ui.forecast_scroll, 1) # scroll down


def on_sel():
    # gpiozero fires both held and released for a long press, release must be ignored if sel_held_handler ran
    if ui.sel_was_held:
        ui.sel_was_held = False
        return

    _note_input()

    if ui.mode == MODE_IDLE:
        ui.mode = MODE_STATUS
        return

    if ui.mode == MODE_STATUS:
        ui.mode = MODE_MENU
        ui.menu_idx = 0

    elif ui.mode == MODE_MENU:
        _, action = menu[ui.menu_idx]
        do_menu_action(action)

    elif ui.mode == MODE_WHEN:
        if ui.when_field == "hours":
            ui.when_field = "minutes"
        else:
            commit_pending_log()


def _sel_held_handler():
    _note_input()
    ui.sel_was_held = True

    # Hold SEL on Status -> go back to idle
    if ui.mode == MODE_STATUS:
        show_toast("Back to idle...")
        ui.mode = MODE_IDLE
        return

    # Hold SEL on Menu -> return to Status
    if ui.mode == MODE_MENU:
        show_toast("Back to status...")
        ui.mode = MODE_STATUS
        return

    # Hold SEL on When -> cancel and return to Menu
    if ui.mode == MODE_WHEN:
        show_toast(["Canceled", "Back to menu..."])
        ui.pending_log_value = None
        ui.mode = MODE_MENU
        return

    # Hold SEL on Weather -> back to menu
    if ui.mode == MODE_WEATHER:
        show_toast("Back to menu...")
        ui.menu_idx = _menu_index_for("weather")
        ui.mode = MODE_MENU
        return

    # Hold SEL on Forecast -> back to menu
    if ui.mode == MODE_FORECAST:
        show_toast("Back to menu...")
        ui.menu_idx = _menu_index_for("forecast")
        ui.mode = MODE_MENU
        return


# ----------------------------
# Wire callbacks
# ----------------------------
BTN_UP.when_pressed    = on_up
BTN_DOWN.when_pressed  = on_down
BTN_SEL.hold_time      = 0.6
BTN_SEL.when_held      = _sel_held_handler
BTN_SEL.when_released  = on_sel
