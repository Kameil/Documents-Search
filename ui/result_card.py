"""
ui/result_card.py
-----------------
Widget GTK que exibe um único resultado de busca (SearchResult)
como um card visual com score, nome do documento e trecho de texto.
"""

from __future__ import annotations

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from core.vector_store import SearchResult


class ResultCard(Gtk.Box):
    """Card visual para exibir um SearchResult."""

    def __init__(self, result: SearchResult, rank: int) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_style_context().add_class("result-card")

        # --- Linha superior: rank + nome do doc + score ---
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        rank_label = Gtk.Label(label=f"#{rank}")
        rank_label.get_style_context().add_class("result-score")
        rank_label.set_halign(Gtk.Align.START)

        doc_label = Gtk.Label(label=result.doc_name)
        doc_label.get_style_context().add_class("result-docname")
        doc_label.set_halign(Gtk.Align.START)
        doc_label.set_hexpand(True)
        doc_label.set_ellipsize(3)       # PANGO_ELLIPSIZE_END = 3
        doc_label.set_tooltip_text(result.doc_path)

        score_label = Gtk.Label(label=f"dist: {result.score:.4f}")
        score_label.get_style_context().add_class("result-score")
        score_label.set_halign(Gtk.Align.END)

        header.append(rank_label)
        header.append(doc_label)
        header.append(score_label)

        # --- Separador ---
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        # --- Trecho de texto ---
        text_label = Gtk.Label(label=self._truncate(result.text, 400))
        text_label.get_style_context().add_class("result-text")
        text_label.set_line_wrap(True)
        text_label.set_xalign(0.0)
        text_label.set_selectable(True)

        self.append(header)
        self.append(sep)
        self.append(text_label)

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        return text if len(text) <= max_chars else text[:max_chars].rstrip() + "…"
