"""
ui/sidebar.py
-------------
Painel lateral com a lista de documentos indexados
e botões para adicionar / remover documentos.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class Sidebar(Gtk.Box):
    """Painel lateral de gerenciamento de documentos."""

    def __init__(
        self,
        on_add_files: Callable[[list[Path]], None],
        on_clear_index: Callable[[], None],
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_style_context().add_class("sidebar")
        self.set_size_request(220, -1)

        self._on_add_files = on_add_files
        self._on_clear_index = on_clear_index

        self._build_ui()

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Título
        title = Gtk.Label(label="📁  Documentos")
        title.set_halign(Gtk.Align.START)
        title.get_style_context().add_class("result-docname")
        title.set_margin_top(8)
        title.set_margin_start(8)
        self.pack_start(title, False, False, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.pack_start(sep, False, False, 4)

        # Lista rolável
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        self._listbox = Gtk.ListBox()
        self._listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.add(self._listbox)
        self.pack_start(scroll, True, True, 0)

        # Label de status (total)
        self._count_label = Gtk.Label(label="0 documentos · 0 chunks")
        self._count_label.get_style_context().add_class("status-label")
        self._count_label.set_halign(Gtk.Align.CENTER)
        self.pack_start(self._count_label, False, False, 4)

        # Botões
        btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        btn_box.set_margin_start(6)
        btn_box.set_margin_end(6)
        btn_box.set_margin_bottom(10)

        self._add_btn = Gtk.Button(label="＋  Adicionar arquivos")
        self._add_btn.get_style_context().add_class("btn-primary")
        self._add_btn.connect("clicked", self._on_add_clicked)

        self._clear_btn = Gtk.Button(label="🗑  Limpar índice")
        self._clear_btn.get_style_context().add_class("btn-secondary")
        self._clear_btn.connect("clicked", self._on_clear_clicked)

        btn_box.pack_start(self._add_btn, False, False, 0)
        btn_box.pack_start(self._clear_btn, False, False, 0)
        self.pack_start(btn_box, False, False, 0)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_add_clicked(self, _btn: Gtk.Button) -> None:
        dialog = Gtk.FileChooserDialog(
            title="Selecionar documentos",
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog.set_select_multiple(True)

        # Filtro de tipos suportados
        file_filter = Gtk.FileFilter()
        file_filter.set_name("Documentos suportados")
        for pat in ("*.pdf", "*.docx", "*.txt", "*.md", "*.xlsx"):
            file_filter.add_pattern(pat)
        dialog.add_filter(file_filter)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            paths = [Path(p) for p in dialog.get_filenames()]
            self._on_add_files(paths)
        dialog.destroy()

    def _on_clear_clicked(self, _btn: Gtk.Button) -> None:
        confirm = Gtk.MessageDialog(
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Limpar índice?",
            secondary_text="Todos os embeddings serão removidos. Esta ação não pode ser desfeita.",
        )
        if confirm.run() == Gtk.ResponseType.YES:
            self._on_clear_index()
        confirm.destroy()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def add_document_row(self, name: str, chunks: int) -> None:
        """Adiciona uma linha na lista de documentos."""
        row = Gtk.ListBoxRow()
        row.get_style_context().add_class("doc-row")

        label = Gtk.Label(label=f"{name}  ({chunks} chunks)")
        label.set_halign(Gtk.Align.START)
        label.set_ellipsize(3)
        row.add(label)

        self._listbox.add(row)
        self._listbox.show_all()

    def clear_document_list(self) -> None:
        """Remove todas as linhas da lista."""
        for row in self._listbox.get_children():
            self._listbox.remove(row)

    def update_count(self, n_docs: int, n_chunks: int) -> None:
        """Atualiza o label de contagem."""
        self._count_label.set_text(f"{n_docs} doc(s) · {n_chunks} chunks")

    def set_loading(self, loading: bool) -> None:
        """Desabilita/habilita os botões durante indexação."""
        self._add_btn.set_sensitive(not loading)
        self._clear_btn.set_sensitive(not loading)
