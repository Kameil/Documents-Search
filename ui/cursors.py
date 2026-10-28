"""Helpers for pointer feedback in GTK widgets."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


def use_hand_cursor(widget: Gtk.Widget) -> None:
    """Show a hand cursor while a clickable widget is hovered."""
    controller = Gtk.EventControllerMotion.new()
    controller.connect("enter", _set_hand_cursor, widget)
    controller.connect("leave", _clear_cursor, widget)
    widget.add_controller(controller)


def _set_hand_cursor(_controller: Gtk.EventControllerMotion, _x: float, _y: float, widget: Gtk.Widget) -> None:
    widget.set_cursor_from_name("pointer")


def _clear_cursor(_controller: Gtk.EventControllerMotion, widget: Gtk.Widget) -> None:
    widget.set_cursor(None)
