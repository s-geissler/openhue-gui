# OpenHue GUI

A lightweight system tray application for controlling Philips Hue lights via the [openhue](https://github.com/openhue/openhue-cli) CLI.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Quick Access** — Left-click the tray icon to see and activate modes
- **Color Picker** — Visual color selection in the mode editor
- **Dynamic Icon** — Tray icon tints to show the current mode's color
- **Flexible Configuration** — Edit modes via GUI or directly in JSON
- **Light/Room Support** — Toggle between targeting lights or rooms

## Requirements

- Python 3.8+
- [openhue](https://github.com/openhue/openhue-cli) CLI installed and configured
- GTK3 with libappindicator
- Pillow

### Ubuntu/Debian

```bash
sudo apt install gir1.2-appindicator3-0.1 python3-gi python3-gi-gtk3
pip install Pillow PyGObject
```

### Fedora

```bash
sudo dnf install libappindicator-gtk3 python3-gobject gtk3
pip install Pillow PyGObject
```

### Arch

```bash
sudo pacman -S libappindicator python-gobject python-cairo
pip install Pillow PyGObject
```

## Installation

```bash
git clone https://github.com/s-geissler/openhue-gui.git
cd openhue-gui
python3 main.py
```

## Usage

### Modes

A mode consists of:
- **Name** — Display label
- **Target** — Light or room name (empty = all)
- **Type** — `light` or `room`
- **Command** — openhue arguments (e.g., `--on --rgb #FF9933 --brightness 60`)
- **Color** — Hex color for the swatch and icon tinting

### Controls

- **Left-click tray icon** — Open mode selection popup
- **Right-click tray icon** — Open menu (modes, edit, exit)

### Config File

Modes are stored in `~/.config/openhue-gui/modes.json`:

```json
{
  "version": 1,
  "modes": [
    {
      "id": "uuid",
      "name": "Cozy Orange",
      "command": "--rgb #FF9933 --brightness 60",
      "target": "",
      "target_type": "light",
      "color": "#FF9933"
    }
  ]
}
```