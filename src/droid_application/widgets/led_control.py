import weakref
from nicegui import ui


class LedControlWidget:
    def __init__(self, parent=None) -> None:
        self.parent = weakref.proxy(parent) if parent is not None else None

        self.button: ui.button = None
        self.button_is_on: bool = False

        self.rate_select: ui.number = None

        self.led: ui.element = None
        self.led_is_lit: bool = False
        self.led_timer = None

        ui.label(text='LED Controls').classes('text-md font-medium')
        with ui.row().classes('items-center gap-4'):
            self.button = ui.button(
                text='OFF',
                on_click=self.on_toggle
            ).props('push color=grey outline')

            self.rate_select = ui.number(
                label='Rate (Hz)',
                value=1,
                min=1,
                max=10,
                step=1,
                format='%.0f',  # <-- changed from %.0i
            ).classes('w-15')
            self.rate_select.on('change', self.on_rate_select_change)
            self.rate_select.on('blur', self.on_rate_select_change)
            self.rate_select.on('keydown.enter', self.on_rate_select_change)

            self.led = ui.element('div').classes(
                'w-6 h-6 rounded-full bg-gray-700 border border-gray-500'
            )

            # Timer toggles ONLY the LED (not the button)
            self.led_timer = ui.timer(
                interval=0.5,
                callback=self._on_led_tick,
                active=False
            )

        # apply initial LED state
        self._set_led_color(False)

    def on_toggle(self, e=None) -> None:
        """Button click: enable/disable blinking."""
        self.button_is_on = not self.button_is_on

        if self.button_is_on:
            self.button.text = 'ON'
            self.button.props('push color=green')

            # Start blinking
            self.led_is_lit = False
            self._set_led_color(False)
            self._update_timer_interval_from_rate()
            self.led_timer.active = True
        else:
            self.button.text = 'OFF'
            self.button.props('push color=grey outline')

            # Stop blinking and force LED OFF
            self.led_timer.active = False
            self.led_is_lit = False
            self._set_led_color(False)

    def on_rate_select_change(self, e=None) -> None:
        """Rate change: clamp/snap and update timer interval."""
        # clamp and snap value
        rate = self._get_clamped_rate()
        if self.rate_select.value != rate:
            self.rate_select.set_value(rate)

        # only matters if we're currently blinking
        if self.button_is_on:
            self._update_timer_interval_from_rate()

    def _get_clamped_rate(self) -> float:
        try:
            v = float(self.rate_select.value) if self.rate_select.value is not None else 1.0
        except (TypeError, ValueError):
            v = 1.0
        return max(1.0, min(10.0, v))

    def _update_timer_interval_from_rate(self) -> None:
        """Hz = full on/off cycles per second, so toggle every half-period."""
        hz = self._get_clamped_rate()
        self.led_timer.interval = 1.0 / (2.0 * hz)

    def _on_led_tick(self) -> None:
        """Timer callback: flip LED visual state."""
        self.led_is_lit = not self.led_is_lit
        self._set_led_color(self.led_is_lit)

    def _set_led_color(self, is_lit: bool) -> None:
        if is_lit:
            self.led.classes(
                remove='bg-gray-700 border-gray-500',
                add='bg-blue-500 border-blue-300 shadow-lg'
            )
        else:
            self.led.classes(
                remove='bg-blue-500 border-blue-300 shadow-lg',
                add='bg-gray-700 border-gray-500'
            )
