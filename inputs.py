"""Input handling — button callbacks and wiring."""

import time

from hardware import BTN_UP, BTN_DOWN, BTN_SEL, device, SCREEN_FONT
from idle import _cycle_font
from screens import (
    ui,
    MODE_IDLE, MODE_STATUS, MODE_MENU, MODE_WHEN, MODE_WEATHER, MODE_FORECAST,
    menu, MINUTES_OPTIONS, MAX_WHEN_HOURS,
    do_menu_action, commit_pending_log, show_toast, weather_lines, forecast_lines,
)


def _register_input_and_maybe_wake():
    """Mark activity; return True if the press was consumed just to wake from idle."""
    ui.last_input_t = time.monotonic()
    if ui.mode == MODE_IDLE:
        ui.mode = MODE_STATUS
        return True
    return False


def on_up():
    # when the system is idling we do not want any button other than select
    # to interrupt the animation.  the up button has no effect in that state
    # so just ignore it entirely (this makes the behaviour symmetric with
    # on_down, and keeps font‑cycling free of spurious wakeups).
    if ui.mode == MODE_IDLE:
        return

    if _register_input_and_maybe_wake():
        return

    if ui.mode == MODE_MENU:
        ui.menu_idx = (ui.menu_idx - 1) % len(menu)

    elif ui.mode == MODE_WHEN:
        if ui.when_field == "hours":
            ui.when_hours = (ui.when_hours + 1) % (MAX_WHEN_HOURS + 1)
        else:
            ui.when_min_idx = (ui.when_min_idx + 1) % len(MINUTES_OPTIONS)

    elif ui.mode == MODE_WEATHER:
        lines = weather_lines()
        bbox = SCREEN_FONT.getbbox("Ag")
        font_h = bbox[3] - bbox[1]
        line_h = font_h + 1
        max_lines = device.height // line_h
        max_scroll = max(0, len(lines) - max_lines)
        ui.weather_scroll = max(0, min(ui.weather_scroll - 1, max_scroll))

    elif ui.mode == MODE_FORECAST:
        lines = forecast_lines()
        bbox = SCREEN_FONT.getbbox("Ag")
        font_h = bbox[3] - bbox[1]
        line_h = font_h + 1
        max_lines = device.height // line_h
        max_scroll = max(0, len(lines) - max_lines)
        ui.forecast_scroll = max(0, min(ui.forecast_scroll - 1, max_scroll))


def on_down():
    if ui.mode == MODE_IDLE:
        _cycle_font()
        return

    if _register_input_and_maybe_wake():
        return

    if ui.mode == MODE_MENU:
        ui.menu_idx = (ui.menu_idx + 1) % len(menu)

    elif ui.mode == MODE_WHEN:
        if ui.when_field == "hours":
            ui.when_hours = (ui.when_hours - 1) % (MAX_WHEN_HOURS + 1)
        else:
            ui.when_min_idx = (ui.when_min_idx - 1) % len(MINUTES_OPTIONS)

    elif ui.mode == MODE_WEATHER:
        lines = weather_lines()
        bbox = SCREEN_FONT.getbbox("Ag")
        font_h = bbox[3] - bbox[1]
        line_h = font_h + 1
        max_lines = device.height // line_h
        max_scroll = max(0, len(lines) - max_lines)
        ui.weather_scroll = min(max_scroll, ui.weather_scroll + 1)

    elif ui.mode == MODE_FORECAST:
        lines = forecast_lines()
        bbox = SCREEN_FONT.getbbox("Ag")
        font_h = bbox[3] - bbox[1]
        line_h = font_h + 1
        max_lines = device.height // line_h
        max_scroll = max(0, len(lines) - max_lines)
        ui.forecast_scroll = min(max_scroll, ui.forecast_scroll + 1)


def on_sel():
    # Ignore the release if the button was held (hold = cancel)
    if ui.sel_was_held:
        ui.sel_was_held = False
        return

    # select is the *only* button that wakes the display from idle.  when
    # we detect an idle press we skip the normal wake helper and return the
    # UI to the status screen (the caller may press SEL again to enter the
    # menu).  this keeps behaviour consistent with the other buttons which
    # also wake to status.
    if ui.mode == MODE_IDLE:
        ui.last_input_t = time.monotonic()
        ui.mode = MODE_STATUS
        return

    if _register_input_and_maybe_wake():
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

    # Hold SEL on When -> cancel and return to Status
    if ui.mode == MODE_WHEN:
        show_toast(["Canceled", "Back to menu..."])
        ui.pending_log_value = None
        ui.mode = MODE_STATUS
        return

    # Hold SEL on Weather -> back to menu
    if ui.mode == MODE_WEATHER:
        show_toast("Back to menu...")
        # select the "Weather" menu item if present
        idx = next((i for i, (_, a) in enumerate(menu) if a.get("type") == "weather"), 0)
        ui.menu_idx = idx
        ui.mode = MODE_MENU
        return

    # Hold SEL on Forecast -> back to menu
    if ui.mode == MODE_FORECAST:
        show_toast("Back to menu...")
        idx = next((i for i, (_, a) in enumerate(menu) if a.get("type") == "forecast"), 0)
        ui.menu_idx = idx
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

