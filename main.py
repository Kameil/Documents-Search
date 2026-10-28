"""
main.py
-------
Ponto de entrada da aplicação Search in Documents.

Uso:
    python main.py
"""

from __future__ import annotations

import sys

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

from ui.main_window import MainWindow
from ui.styles import apply_css


class SearchApp(Gtk.Application):
    """Aplicação GTK principal."""

    def __init__(self) -> None:
        super().__init__(
            application_id="com.example.search_in_documents",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self._window: MainWindow | None = None
        self.connect("activate", self._on_activate)

    def _on_activate(self, app: "SearchApp") -> None:
        if self._window is None:
            # Aplica o CSS global antes de criar a janela
            apply_css()
            self._window = MainWindow(app)
        self._window.present()


def main() -> int:
    app = SearchApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
