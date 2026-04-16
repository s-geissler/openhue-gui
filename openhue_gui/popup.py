"""Mode selection popup window."""

import subprocess
import logging

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango

from .modes_schema import Mode, Config

logger = logging.getLogger(__name__)


def _parse_hex_color(hex_color: str) -> Gdk.RGBA:
    """Parse a hex color string to GdkRGBA."""
    rgba = Gdk.RGBA()
    if not rgba.parse(hex_color):
        rgba.parse("#FFFFFF")  # fallback
    return rgba


def show_popup(app_ref, config: Config, on_mode_selected) -> None:
    """Show the mode selection popup near the tray icon."""
    popup = ModePopup(app_ref, config, on_mode_selected)
    popup.show_all()


class ModePopup(Gtk.Window):
    def __init__(self, app_ref, config: Config, on_mode_selected):
        super().__init__(
            title="OpenHue",
            type=Gtk.WindowType.POPUP,
            skip_taskbar_hint=True,
            skip_pager_hint=True,
            resizable=False,
            decorated=False,
            border_width=8,
        )

        self.app_ref = app_ref
        self.config = config
        self.on_mode_selected = on_mode_selected

        self._setup_ui()
        self._position_near_tray()

        # Connect click-outside detection
        self.connect("button-press-event", self._on_button_press)
        self.connect("focus-out-event", self._on_focus_out)

    def _setup_ui(self):
        """Build the popup UI."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.add(box)

        for mode in self.config.modes:
            btn = self._create_mode_button(mode)
            box.pack_start(btn, False, False, 0)

        if not self.config.modes:
            label = Gtk.Label(label="No modes configured")
            label.set_sensitive(False)
            box.pack_start(label, False, False, 0)

    def _create_mode_button(self, mode: Mode) -> Gtk.Button:
        """Create a button for a single mode."""
        btn = Gtk.Button(relief=Gtk.ReliefStyle.HALF)
        btn.set_can_focus(False)

        # Create hbox with color swatch + label
        hbox = Gtk.Box(spacing=8)
        btn.add(hbox)

        # Color swatch
        swatch = Gtk.DrawingArea()
        swatch.set_size_request(20, 20)
        swatch.connect("draw", self._draw_swatch, mode.color)
        hbox.pack_start(swatch, False, False, 0)

        # Label
        label = Gtk.Label(label=mode.name)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        hbox.pack_start(label, True, True, 0)

        btn.connect("clicked", lambda _: self._activate_mode(mode))

        return btn

    def _draw_swatch(self, area, cr, color_hex):
        """Draw the color swatch."""
        rgba = _parse_hex_color(color_hex)
        alloc = area.get_allocation()
        cr.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
        cr.rectangle(0, 0, alloc.width, alloc.height)
        cr.fill()

    def _activate_mode(self, mode: Mode):
        """Activate a mode and close popup."""
        self.hide()
        self.on_mode_selected(mode)

    def _position_near_tray(self):
        """Position the popup near the tray icon."""
        # Try to get tray icon position via Gdk
        screen = Gdk.Screen.get_default()
        display = Gdk.Display.get_default()

        # Find the tray icon window
        # This is a simplification - actual implementation may need
        # platform-specific code to find the tray icon position
        # For now, position at cursor location
        seat = display.get_default_seat()
        pointer = seat.get_pointer()
        screen, x, y = pointer.get_position()

        # Position popup near cursor, offset slightly
        self.move(int(x) - 50, int(y) - 100)

    def _on_button_press(self, widget, event):
        """Handle button press events."""
        # Allow the button press to propagate for click-outside detection
        return False

    def _on_focus_out(self, widget, event):
        """Close popup when it loses focus."""
        self.hide()
        return True