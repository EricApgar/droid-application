#!/usr/bin/env python3

from nicegui import ui
from gpiozero import LED


# ---------- Domain / state layer ----------

class DroidState:
    """Holds the logical state of the droid's LED behavior."""
    def __init__(self, enabled: bool = False, flash_rate_hz: float = 1.0):
        self.enabled = enabled
        self.flash_rate_hz = flash_rate_hz


class LEDController:
    """Hardware abstraction for the LED on GPIO 17."""
    def __init__(self, gpio_pin: int = 17):
        self.led = LED(gpio_pin)

    def apply_state(self, state: DroidState) -> None:
        """Apply the logical state to the physical LED."""
        if not state.enabled or state.flash_rate_hz <= 0:
            # LED off if disabled or invalid rate
            self.led.off()
            return

        period = 1.0 / state.flash_rate_hz  # seconds per cycle
        on_time = period / 2.0
        off_time = period / 2.0

        # gpiozero handles blinking in a background thread
        self.led.blink(on_time=on_time, off_time=off_time, background=True)


# Instantiate global-ish objects for this simple app
state = DroidState()
led_controller = LEDController(gpio_pin=17)


# ---------- UI / interaction layer ----------

def update_hardware() -> None:
    """Push current state into the hardware layer."""
    led_controller.apply_state(state)


def on_toggle_change(e) -> None:
    """Handle changes to the On/Off switch."""
    state.enabled = bool(e.value)
    update_hardware()


def on_rate_change(e) -> None:
    """Handle changes to the flash rate number input."""
    try:
        # NiceGUI's ui.number passes e.value as a number or None
        value = float(e.value) if e.value is not None else 0.0
    except (TypeError, ValueError):
        value = 0.0

    # Clamp to sane limits
    if value < 0:
        value = 0.0
    if value > 50:  # arbitrary upper bound; we can adjust later
        value = 50.0

    state.flash_rate_hz = value
    update_hardware()


# ---------- Build the NiceGUI interface ----------

with ui.row().classes('items-center gap-4 p-4'):
    # On/Off control
    led_switch = ui.switch('LED On/Off', value=state.enabled)
    led_switch.on('change', on_toggle_change)

    # Flash rate number input with up/down arrows
    rate_input = ui.number(
        label='Flash Rate (Hz)',
        value=state.flash_rate_hz,
        step=0.5,
        min=0.0,
        max=50.0,
        format='%.1f',
    )
    rate_input.on('change', on_rate_change)

# Optional: show current values as text (useful while debugging)
with ui.row().classes('items-center gap-2 px-4 pb-4'):
    ui.label('Current state:')
    ui.label().bind_text_from(state, 'enabled', lambda v: f'On: {v}')
    ui.label().bind_text_from(state, 'flash_rate_hz',
                              lambda v: f'Rate: {v:.1f} Hz')

# Start the app; you can open it in a browser on the Pi
ui.run(host='0.0.0.0', port=8080, reload=False, show=False)
