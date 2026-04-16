#!/usr/bin/env python3
"""Main entry point for openhue-gui."""

import subprocess
import logging
import tempfile
import signal
import sys
from pathlib import Path
from importlib.resources import files

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, AppIndicator3

from PIL import Image

from .config import load_config
from .modes_schema import Mode
from .popup import show_popup
from .editor import show_editor
from .notify import notify_success, notify_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_icon_path() -> str:
    """Get the path to the bundled tray icon.

    Uses importlib.resources to locate the icon whether running
    from source (dev mode) or installed package.
    """
    # Try importlib.resources first (Python 3.9+)
    if sys.version_info >= (3, 9):
        try:
            icon_path = files("openhue_gui").joinpath("icons", "tray-icon.png")
            if icon_path.is_file():
                return str(icon_path)
        except Exception:
            pass

    # Fallback for dev mode: look relative to this file
    dev_path = Path(__file__).parent / "icons" / "tray-icon.png"
    if dev_path.is_file():
        return str(dev_path)

    # Final fallback: original hardcoded path (shouldn't reach here)
    return "/usr/share/openhue-gui/icons/tray-icon.png"


def _sigint_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    logger.info("Received Ctrl+C, shutting down...")
    Gtk.main_quit()

ICON_PATH = _get_icon_path()


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_tinted_icon(base_icon_path: str, hex_color: str, output_path: str) -> None:
    """Create a tinted version of the base icon."""
    try:
        # Parse hex color
        target_rgb = hex_to_rgb(hex_color)
        target_color = tuple(c / 255.0 for c in target_rgb)

        # Load base icon
        img = Image.open(base_icon_path).convert("RGBA")

        # Create tinted version
        pixels = img.load()
        width, height = img.size

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                if a > 0:  # Not transparent
                    # Blend with target color
                    blend = 0.7  # How much to blend (0=black, 1=target)
                    new_r = int(r * (1 - blend) + target_color[0] * 255 * blend)
                    new_g = int(g * (1 - blend) + target_color[1] * 255 * blend)
                    new_b = int(b * (1 - blend) + target_color[2] * 255 * blend)
                    pixels[x, y] = (new_r, new_g, new_b, a)

        img.save(output_path, "PNG")
    except Exception as e:
        logger.error(f"Failed to create tinted icon: {e}")


class OpenHueApp:
    def __init__(self):
        self.config = load_config()
        self.indicator = self._create_tray_icon()
        self.popup_window = None
        self.current_icon_path = ICON_PATH
        self._temp_icons = []  # Track temp files for cleanup

    def _create_tray_icon(self) -> AppIndicator3.Indicator:
        """Create the system tray indicator."""
        indicator = AppIndicator3.Indicator.new(
            "openhue-gui",
            "openhue-gui",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        indicator.set_icon(ICON_PATH)
        indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        indicator.set_menu(self._create_menu())

        # Connect to the actor for left-click handling
        # Note: libappindicator doesn't directly support left-click callbacks
        # We use a GtkStatusIcon approach via the actor if available
        try:
            actor = indicator.get_actor()
            if actor:
                actor.connect("button-press-event", self._on_actor_clicked)
        except Exception:
            pass

        return indicator

    def _update_tray_icon(self, hex_color: str) -> None:
        """Update the tray icon to show the given color."""
        try:
            # Create tinted icon in temp file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                temp_path = f.name

            create_tinted_icon(ICON_PATH, hex_color, temp_path)

            # Set as indicator icon
            self.indicator.set_icon(temp_path)

            # Track for cleanup
            self._temp_icons.append(temp_path)
            if len(self._temp_icons) > 10:  # Keep only recent 10
                old = self._temp_icons.pop(0)
                try:
                    Path(old).unlink()
                except:
                    pass

        except Exception as e:
            logger.error(f"Failed to update tray icon: {e}")

    def _on_actor_clicked(self, actor, event):
        """Handle click on the tray icon actor."""
        if event.button == 1:  # Left click
            self._show_mode_popup()
        return False

    def _show_mode_popup(self):
        """Show the mode selection popup."""
        if self.popup_window is None or not self.popup_window.get_visible():
            self.popup_window = ModePopup(self, self.config, self.run_command)
            self.popup_window.show_all()

    def _create_menu(self) -> Gtk.Menu:
        """Create the right-click menu."""
        menu = Gtk.Menu.new()

        # Add modes directly to menu
        if self.config.modes:
            for mode in self.config.modes:
                item = Gtk.MenuItem.new_with_label(f"{mode.name}")
                item.connect("activate", lambda _, m=mode: self._run_mode(m))
                menu.append(item)
        else:
            item = Gtk.MenuItem.new_with_label("No modes configured")
            item.set_sensitive(False)
            menu.append(item)

        menu.append(Gtk.SeparatorMenuItem.new())

        edit_item = Gtk.MenuItem.new_with_label("Edit Modes...")
        edit_item.connect("activate", lambda _: self._open_editor())
        menu.append(edit_item)

        exit_item = Gtk.MenuItem.new_with_label("Exit")
        exit_item.connect("activate", lambda _: self._quit())
        menu.append(exit_item)

        menu.show_all()
        return menu

    def _run_mode(self, mode: Mode):
        """Run a mode's command."""
        self.run_command(mode)

    def _open_editor(self) -> None:
        """Open the mode editor window."""
        show_editor(self.config, self._on_config_changed)

    def _on_config_changed(self, config) -> None:
        """Called when config is saved in editor."""
        self.config = config
        # Rebuild menu to reflect new modes
        self.indicator.set_menu(self._create_menu())

    def _quit(self) -> None:
        """Exit the application."""
        # Cleanup temp icons
        for path in self._temp_icons:
            try:
                Path(path).unlink()
            except:
                pass
        Gtk.main_quit()

    def run_command(self, mode: Mode) -> None:
        """Execute a mode's openhue command."""
        target = mode.target.strip()
        target_type = mode.target_type if hasattr(mode, 'target_type') and mode.target_type else "light"

        # Escape # to \# to prevent shell from interpreting it as comment
        escaped_command = mode.command.replace("#", "\\#")

        if target:
            cmd = f"openhue set {target_type} {target} {escaped_command}"
        else:
            cmd = f"openhue set {target_type} {escaped_command}"

        logger.info(f"Executing: {cmd}")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            logger.info(f"Result: returncode={result.returncode}")
            if result.stdout:
                logger.info(f"stdout: {result.stdout}")
            if result.stderr:
                logger.info(f"stderr: {result.stderr}")
            if result.returncode == 0:
                notify_success(mode.name)
                # Update tray icon to show mode color
                self._update_tray_icon(mode.color)
            else:
                notify_error(mode.name, result.stderr)
        except subprocess.TimeoutExpired:
            notify_error(mode.name, "Command timed out")
        except FileNotFoundError:
            notify_error(mode.name, "openhue CLI not found")

    def run(self) -> None:
        """Start the application."""
        logger.info("OpenHue GUI started")
        Gtk.main()


# Import ModePopup here for use in this module
from .popup import ModePopup


def main():
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, _sigint_handler)
    app = OpenHueApp()
    app.run()


if __name__ == "__main__":
    main()
