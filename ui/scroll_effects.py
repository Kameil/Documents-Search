"""Native kinetic and elastic scrolling configuration for GTK 4."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


def enable_elastic_scrolling(scroll: Gtk.ScrolledWindow) -> None:
    """Enable GTK 4's native kinetic scrolling and elastic overscroll."""
    scroll.set_kinetic_scrolling(True)
    scroll.set_overlay_scrolling(True)
