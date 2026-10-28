"""
ui/sidebar.py
-------------
Painel lateral com a lista de documentos indexados
e botões para adicionar / remover documentos.
"""

from __future__ import annotations

import os
import subprocess
import threading
from collections.abc import Callable
from pathlib import Path

import gi

from config import config
from ui.cursors import use_hand_cursor
from ui.scroll_effects import enable_elastic_scrolling

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402


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
        title.get_style_context().add_class("sidebar-title")
        title.set_margin_top(10)
        title.set_margin_start(10)
        self.append(title)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(sep)

        # Lista rolável
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        enable_elastic_scrolling(scroll)

        self._listbox = Gtk.ListBox()
        self._listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.set_child(self._listbox)
        self.append(scroll)

        # Label de status (total)
        self._count_label = Gtk.Label(label="0 documentos · 0 chunks")
        self._count_label.get_style_context().add_class("status-label")
        self._count_label.set_halign(Gtk.Align.CENTER)
        self.append(self._count_label)

        # Botões
        btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        btn_box.set_margin_start(6)
        btn_box.set_margin_end(6)
        btn_box.set_margin_bottom(10)

        self._add_btn = Gtk.Button(label="＋  Adicionar arquivos")
        self._add_btn.get_style_context().add_class("btn-primary")
        use_hand_cursor(self._add_btn)
        self._add_btn.connect("clicked", self._on_add_clicked)

        self._add_folder_btn = Gtk.Button(label="📁  Adicionar pasta")
        self._add_folder_btn.get_style_context().add_class("btn-primary")
        use_hand_cursor(self._add_folder_btn)
        self._add_folder_btn.connect("clicked", self._on_add_folder_clicked)

        self._clear_btn = Gtk.Button(label="🗑  Limpar índice")
        self._clear_btn.get_style_context().add_class("btn-secondary")
        use_hand_cursor(self._clear_btn)
        self._clear_btn.connect("clicked", self._on_clear_clicked)

        btn_box.append(self._add_btn)
        btn_box.append(self._add_folder_btn)
        btn_box.append(self._clear_btn)
        self.append(btn_box)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_add_clicked(self, _btn: Gtk.Button) -> None:
        """Seleciona um ou mais documentos usando o seletor nativo do sistema."""
        print("Abrindo seletor de arquivos do sistema…")
        self._add_btn.set_sensitive(False)
        thread = threading.Thread(target=self._choose_files_thread, daemon=True)
        thread.start()

    def _choose_files_thread(self) -> None:
        patterns = " ".join(f"*{extension}" for extension in config.supported_extensions)
        result = subprocess.run(
            [
                "kdialog",
                "--getopenfilename",
                str(Path.home()),
                f"{patterns}|Documentos suportados",
                "--multiple",
                "--separate-output",
                "--title",
                "Selecionar documentos",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        GLib.idle_add(
            self._on_files_chooser_complete,
            result.returncode,
            result.stdout,
            result.stderr.strip(),
        )

    def _on_files_chooser_complete(self, returncode: int, output: str, error: str) -> bool:
        self._add_btn.set_sensitive(True)
        if returncode == 1 and not error:
            print("Seleção de arquivos cancelada.")
            return False
        if returncode != 0:
            print(
                "Erro ao abrir o seletor de arquivos "
                f"(código {returncode}): {error or 'erro desconhecido'}"
            )
            return False

        paths = [Path(path) for path in output.splitlines() if path]
        paths = [
            path
            for path in paths
            if path.is_file() and path.suffix.lower() in config.supported_extensions
        ]
        if not paths:
            print("Nenhum arquivo suportado selecionado.")
            return False

        print(f"Arquivos selecionados: {paths}")
        self._on_add_files(paths)
        return False

    def _on_add_folder_clicked(self, _btn: Gtk.Button) -> None:
        """Seleciona uma pasta e adiciona todos os documentos suportados nela."""
        print("Abrindo seletor de pasta do sistema…")
        self._add_folder_btn.set_sensitive(False)
        thread = threading.Thread(target=self._choose_folder_thread, daemon=True)
        thread.start()

    def _choose_folder_thread(self) -> None:
        result = subprocess.run(
            [
                "kdialog",
                "--getexistingdirectory",
                str(Path.home()),
                "--title",
                "Selecionar pasta com documentos",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        GLib.idle_add(
            self._on_folder_chooser_complete,
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip(),
        )

    def _on_folder_chooser_complete(self, returncode: int, output: str, error: str) -> bool:
        self._add_folder_btn.set_sensitive(True)
        if returncode == 1 and not error:
            print("Seleção de pasta cancelada.")
            return False  # Usuário cancelou.
        if returncode != 0:
            print(
                "Erro ao abrir o seletor de pasta "
                f"(código {returncode}): {error or 'erro desconhecido'}"
            )
            return False

        folder = Path(output)
        if not folder.is_dir():
            print(f"Pasta selecionada inválida: {folder}")
            return False

        print(f"Pasta selecionada: {folder}")

        paths = self._find_supported_files(folder)
        if not paths:
            self._show_no_documents_message(folder)
            return

        self._on_add_files(paths)
        return False

    @staticmethod
    def _find_supported_files(folder: Path) -> list[Path]:
        """Find readable supported files while safely skipping protected folders."""
        paths: list[Path] = []
        for root, _directories, filenames in os.walk(folder, onerror=lambda _error: None):
            paths.extend(
                Path(root, filename)
                for filename in filenames
                if Path(filename).suffix.lower() in config.supported_extensions
            )
        return sorted(paths, key=lambda path: str(path).lower())

    def _show_no_documents_message(self, folder: Path) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            text="Nenhum documento suportado encontrado",
        )
        dialog.set_secondary_text(f"A pasta '{folder.name}' não contém documentos suportados.")
        dialog.add_button("OK", Gtk.ResponseType.OK)
        dialog.connect("response", lambda dialog, _response: dialog.destroy())
        dialog.show()

    def _on_clear_clicked(self, _btn: Gtk.Button) -> None:
        confirm = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            text="Limpar índice?",
            secondary_text="Todos os embeddings serão removidos. Esta ação não pode ser desfeita.",
        )
        confirm.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        confirm.add_button("Limpar", Gtk.ResponseType.YES)
        confirm.connect("response", self._on_clear_response)
        confirm.show()

    def _on_clear_response(self, dialog: Gtk.MessageDialog, response: int) -> None:
        if response == Gtk.ResponseType.YES:
            self._on_clear_index()
        dialog.destroy()

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
        row.set_child(label)

        self._listbox.append(row)

    def clear_document_list(self) -> None:
        """Remove todas as linhas da lista."""
        row = self._listbox.get_first_child()
        while row:
            next_row = row.get_next_sibling()
            self._listbox.remove(row)
            row = next_row

    def update_count(self, n_docs: int, n_chunks: int) -> None:
        """Atualiza o label de contagem."""
        self._count_label.set_text(f"{n_docs} doc(s) · {n_chunks} chunks")

    def set_loading(self, loading: bool) -> None:
        """Desabilita/habilita os botões durante indexação."""
        self._add_btn.set_sensitive(not loading)
        self._add_folder_btn.set_sensitive(not loading)
        self._clear_btn.set_sensitive(not loading)
