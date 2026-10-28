"""
ui/search_panel.py
------------------
Painel central de busca semântica:
    - Campo de consulta (Entry)
    - Botão de busca
    - Lista de ResultCards
    - Barra de progresso / status
"""

from __future__ import annotations

from typing import Callable

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from core.vector_store import SearchResult
from ui.cursors import use_hand_cursor
from ui.result_card import ResultCard
from ui.scroll_effects import enable_elastic_scrolling


def iter_children(widget: Gtk.Widget):
    child = widget.get_first_child()
    while child:
        next_child = child.get_next_sibling()
        yield child
        child = next_child


class SearchPanel(Gtk.Box):
    """Painel central de busca semântica."""

    def __init__(self, on_search: Callable[[str], None]) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._on_search = on_search
        self._build_ui()

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # --- Área de busca ---
        search_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        search_bar.get_style_context().add_class("search-bar")
        search_bar.set_margin_top(20)
        search_bar.set_margin_start(20)
        search_bar.set_margin_end(20)
        search_bar.set_margin_bottom(10)

        self._entry = Gtk.Entry()
        self._entry.get_style_context().add_class("search-entry")
        self._entry.set_placeholder_text("Digite sua pergunta ou tema para buscar…")
        self._entry.set_hexpand(True)
        self._entry.connect("activate", self._on_entry_activate)

        self._search_btn = Gtk.Button(label="🔍  Buscar")
        self._search_btn.get_style_context().add_class("btn-primary")
        use_hand_cursor(self._search_btn)
        self._search_btn.connect("clicked", self._on_search_clicked)

        search_bar.append(self._entry)
        search_bar.append(self._search_btn)

        # --- Barra de progresso ---
        self._progress = Gtk.ProgressBar()
        self._progress.set_margin_start(20)
        self._progress.set_margin_end(20)
        self._progress.set_show_text(True)
        self._progress.set_text("0%")
        self._progress.hide()

        # --- Label de status ---
        self._status_label = Gtk.Label(label="")
        self._status_label.get_style_context().add_class("status-label")
        self._status_label.set_halign(Gtk.Align.CENTER)

        # --- Área de resultados rolável ---
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        enable_elastic_scrolling(scroll)

        self._results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._results_box.set_margin_start(16)
        self._results_box.set_margin_end(16)
        self._results_box.set_margin_bottom(16)
        scroll.set_child(self._results_box)

        # Montagem
        self.append(search_bar)
        self.append(self._progress)
        self.append(self._status_label)
        self.append(scroll)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_entry_activate(self, _entry: Gtk.Entry) -> None:
        self._trigger_search()

    def _on_search_clicked(self, _btn: Gtk.Button) -> None:
        self._trigger_search()

    def _trigger_search(self) -> None:
        query = self._entry.get_text().strip()
        if query:
            self._on_search(query)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def show_results(self, results: list[SearchResult]) -> None:
        """Exibe lista de resultados substituindo os anteriores."""
        self.clear_results()
        if not results:
            self.set_status("Nenhum resultado encontrado.", "status-label")
            return

        for rank, result in enumerate(results, start=1):
            card = ResultCard(result, rank)
            self._results_box.append(card)

        self.set_status(f"{len(results)} resultado(s) encontrado(s).", "status-success")

    def clear_results(self) -> None:
        """Remove todos os cards de resultado."""
        for child in iter_children(self._results_box):
            self._results_box.remove(child)

    def set_status(self, message: str, css_class: str = "status-label") -> None:
        """Atualiza o label de status."""
        ctx = self._status_label.get_style_context()
        for cls in ("status-label", "status-success", "status-error"):
            ctx.remove_class(cls)
        ctx.add_class(css_class)
        self._status_label.set_text(message)

    def set_searching(self, active: bool) -> None:
        """Ativa/desativa o estado de carregamento."""
        self._search_btn.set_sensitive(not active)
        self._entry.set_sensitive(not active)
        if active:
            self._progress.show()
            self._progress.pulse()
        else:
            self._progress.hide()

    def set_progress(self, fraction: float, message: str = "") -> None:
        """Atualiza a barra de progresso (0.0–1.0)."""
        fraction = max(0.0, min(fraction, 1.0))
        self._progress.show()
        self._progress.set_fraction(fraction)
        self._progress.set_text(f"{fraction:.0%}")
        if message:
            self.set_status(message)
