"""Mode editor window."""

import logging
import uuid

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from .modes_schema import Mode, Config
from .config import save_config

logger = logging.getLogger(__name__)


def show_editor(config: Config, on_save_callback) -> None:
    """Show the mode editor window."""
    editor = ModeEditor(config, on_save_callback)
    editor.show_all()


class ModeEditor(Gtk.Window):
    def __init__(self, config: Config, on_save_callback):
        super().__init__(
            title="OpenHue - Mode Editor",
            default_width=600,
            default_height=400,
            border_width=10,
        )

        self.config = config
        self.on_save_callback = on_save_callback
        self.selected_mode_id = None

        self._setup_ui()
        self._populate_mode_list()
        self.connect("delete-event", lambda w, e: self.hide() or True)

    def _setup_ui(self):
        """Build the editor UI with list + detail panel."""
        main_hbox = Gtk.Box(spacing=10)
        self.add(main_hbox)

        # Left panel: mode list + Add button
        left_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        self.mode_list = Gtk.ListBox()
        self.mode_list.connect("row-selected", self._on_mode_selected)
        self.mode_list.set_vexpand(True)
        left_vbox.pack_start(self.mode_list, True, True, 0)

        add_btn = Gtk.Button(label="+ Add Mode")
        add_btn.connect("clicked", lambda _: self._add_mode())
        left_vbox.pack_start(add_btn, False, False, 0)

        main_hbox.pack_start(left_vbox, True, True, 0)

        # Right panel: detail form
        detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        detail_box.set_hexpand(True)
        main_hbox.pack_start(detail_box, True, True, 0)

        # Detail header
        detail_box.pack_start(Gtk.Label(label="Edit Mode", halign=Gtk.Align.START), False, False, 0)

        # Name field
        name_box = Gtk.Box(spacing=8)
        name_box.pack_start(Gtk.Label(label="Name:", width_chars=8), False, False, 0)
        self.name_entry = Gtk.Entry()
        self.name_entry.set_hexpand(True)
        self.name_entry.connect("changed", self._on_field_changed)
        name_box.pack_start(self.name_entry, True, True, 0)
        detail_box.pack_start(name_box, False, False, 0)

        # Target field
        target_box = Gtk.Box(spacing=8)
        target_box.pack_start(Gtk.Label(label="Target:", width_chars=8), False, False, 0)
        self.target_entry = Gtk.Entry()
        self.target_entry.set_hexpand(True)
        self.target_entry.set_placeholder_text("Light or room name (empty = all)")
        self.target_entry.connect("changed", self._on_field_changed)
        target_box.pack_start(self.target_entry, True, True, 0)
        detail_box.pack_start(target_box, False, False, 0)

        # Target type toggle (light or room)
        type_box = Gtk.Box(spacing=8)
        type_box.pack_start(Gtk.Label(label="Type:", width_chars=8), False, False, 0)
        self.target_type_combo = Gtk.ComboBoxText()
        self.target_type_combo.append("light", "Light")
        self.target_type_combo.append("room", "Room")
        self.target_type_combo.connect("changed", self._on_field_changed)
        type_box.pack_start(self.target_type_combo, False, False, 0)
        detail_box.pack_start(type_box, False, False, 0)

        # Command field
        cmd_box = Gtk.Box(spacing=8)
        cmd_box.pack_start(Gtk.Label(label="Command:", width_chars=8), False, False, 0)
        self.command_entry = Gtk.Entry()
        self.command_entry.set_hexpand(True)
        self.command_entry.set_placeholder_text("--rgb #FF9933 --brightness 60")
        self.command_entry.connect("changed", self._on_field_changed)
        cmd_box.pack_start(self.command_entry, True, True, 0)
        detail_box.pack_start(cmd_box, False, False, 0)

        # Color field with color picker
        color_box = Gtk.Box(spacing=8)
        color_box.pack_start(Gtk.Label(label="Color:", width_chars=8), False, False, 0)
        self.color_button = Gtk.ColorButton()
        self.color_button.set_use_alpha(False)
        self.color_button.connect("color-set", self._on_color_picked)
        color_box.pack_start(self.color_button, False, False, 0)

        # Color hex entry (manual input)
        self.color_entry = Gtk.Entry()
        self.color_entry.set_max_length(7)
        self.color_entry.set_width_chars(8)
        self.color_entry.set_placeholder_text("#FFFFFF")
        self.color_entry.connect("changed", self._on_color_entry_changed)
        color_box.pack_start(self.color_entry, False, False, 0)
        detail_box.pack_start(color_box, False, False, 0)

        # Buttons
        btn_box = Gtk.Box(spacing=8)
        self.save_btn = Gtk.Button(label="Save")
        self.save_btn.connect("clicked", lambda _: self._save_mode())
        self.save_btn.set_sensitive(False)
        btn_box.pack_start(self.save_btn, False, False, 0)

        self.delete_btn = Gtk.Button(label="Delete")
        self.delete_btn.connect("clicked", lambda _: self._delete_mode())
        self.delete_btn.set_sensitive(False)
        btn_box.pack_start(self.delete_btn, False, False, 0)

        detail_box.pack_start(btn_box, False, False, 0)

    def _populate_mode_list(self):
        """Populate the mode list from config."""
        for child in self.mode_list.get_children():
            self.mode_list.remove(child)

        for mode in self.config.modes:
            row = Gtk.ListBoxRow()
            row.add(Gtk.Label(label=mode.name))
            row.mode_id = mode.id
            self.mode_list.add(row)

        self.mode_list.show_all()

    def _on_mode_selected(self, listbox, row):
        """Handle mode selection."""
        if row is None:
            return

        mode_id = row.mode_id
        mode = next((m for m in self.config.modes if m.id == mode_id), None)
        if mode:
            self.selected_mode_id = mode_id
            self.name_entry.set_text(mode.name)
            self.target_entry.set_text(mode.target)
            self.target_type_combo.set_active_id(mode.target_type)
            self.command_entry.set_text(mode.command)
            self.color_entry.set_text(mode.color)
            # Set color button from mode color
            rgba = Gdk.RGBA()
            if rgba.parse(mode.color):
                self.color_button.set_rgba(rgba)
            self.delete_btn.set_sensitive(True)
            self.save_btn.set_sensitive(False)

    def _on_field_changed(self, widget):
        """Handle field changes to enable save."""
        if self.selected_mode_id:
            self.save_btn.set_sensitive(True)

    def _on_color_entry_changed(self, widget):
        """Handle color hex entry changes."""
        color = widget.get_text()
        if self._is_valid_hex(color):
            rgba = Gdk.RGBA()
            if rgba.parse(color):
                self.color_button.set_rgba(rgba)
        if self.selected_mode_id:
            self.save_btn.set_sensitive(True)

    def _on_color_picked(self, widget):
        """Handle color button picker changes - update command if needed."""
        rgba = widget.get_rgba()
        hex_color = f"#{int(rgba.red * 255):02X}{int(rgba.green * 255):02X}{int(rgba.blue * 255):02X}"
        self.color_entry.set_text(hex_color)

        # Update command field if it has --rgb
        cmd = self.command_entry.get_text()
        if "--rgb" in cmd:
            # Replace existing --rgb value
            import re
            new_cmd = re.sub(r"--rgb\s+#[0-9A-Fa-f]{6}", f"--rgb {hex_color}", cmd)
            self.command_entry.set_text(new_cmd)

        if self.selected_mode_id:
            self.save_btn.set_sensitive(True)

    def _is_valid_hex(self, color: str) -> bool:
        """Check if string is a valid hex color."""
        if not color.startswith("#"):
            return False
        if len(color) not in (4, 7):
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False

    def _add_mode(self):
        """Add a new mode."""
        new_mode = Mode(
            id=str(uuid.uuid4()),
            name="New Mode",
            command="--color white",
            target="",
            color="#FFFFFF",
        )
        self.config.modes.append(new_mode)
        self._populate_mode_list()
        # Select the new mode
        for row in self.mode_list.get_children():
            if hasattr(row, 'mode_id') and row.mode_id == new_mode.id:
                self.mode_list.select_row(row)
                break

    def _save_mode(self):
        """Save the currently selected mode."""
        if not self.selected_mode_id:
            return

        mode = next((m for m in self.config.modes if m.id == self.selected_mode_id), None)
        if mode:
            mode.name = self.name_entry.get_text()
            mode.target = self.target_entry.get_text()
            mode.target_type = self.target_type_combo.get_active_id()
            mode.command = self.command_entry.get_text()
            color = self.color_entry.get_text()
            if self._is_valid_hex(color):
                mode.color = color

            save_config(self.config)
            self._populate_mode_list()
            self.save_btn.set_sensitive(False)
            self.on_save_callback(self.config)

    def _delete_mode(self):
        """Delete the currently selected mode."""
        if not self.selected_mode_id:
            return

        # Find and remove mode
        self.config.modes = [m for m in self.config.modes if m.id != self.selected_mode_id]
        save_config(self.config)
        self._populate_mode_list()
        self.name_entry.set_text("")
        self.target_entry.set_text("")
        self.command_entry.set_text("")
        self.color_entry.set_text("")
        self.color_button.set_rgba(Gdk.RGBA(1, 1, 1, 1))
        self.selected_mode_id = None
        self.delete_btn.set_sensitive(False)
        self.save_btn.set_sensitive(False)
        self.on_save_callback(self.config)
