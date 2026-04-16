"""Notification helper using notify-send."""

import subprocess
from typing import Optional


def notify(title: str, message: str, icon: str = "dialog-information") -> None:
    """Show a notification via notify-send."""
    try:
        subprocess.run(
            ["notify-send", title, message, "--icon", icon],
            capture_output=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        pass  # Silently ignore notification failures


def notify_success(mode_name: str) -> None:
    """Show success notification."""
    notify(f"Mode applied: {mode_name}", "OpenHue GUI", "dialog-information")


def notify_error(mode_name: str, error: str = "") -> None:
    """Show error notification."""
    message = f"Failed to apply mode: {mode_name}"
    if error:
        message += f"\n{error}"
    notify("OpenHue Error", message, "dialog-error")
