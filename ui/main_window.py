"""
ui/main_window.py
-----------------
Janela principal da aplicação.

Layout:
    ┌──────────────────────────────────────────┐
    │  HeaderBar (título + botão configurações)│
    ├──────────────┬───────────────────────────┤
    │   Sidebar    │      SearchPanel          │
    │  (docs)      │  (busca + resultados)     │
    └──────────────┴───────────────────────────┘
"""

from __future__ import annotations

import threading
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from config import config
from core.embedder import Embedder
from core.indexer import Indexer
from core.searcher import Searcher
from core.vector_store import VectorStore
from ui.sidebar import Sidebar
from ui.search_panel import SearchPanel


class MainWindow(Gtk.ApplicationWindow):
    """Janela principal da aplicação Search in Documents."""

    def __init__(self, app: Gtk.Application) -> None:
        super().__init__(application=app, title="Search in Documents")
        self.set_default_size(1100, 680)
        self.set_position(Gtk.WindowPosition.CENTER)

        # --- Core ---
        self._store = VectorStore()
        self._embedder = Embedder()
        self._indexer = Indexer(self._store, self._embedder)
        self._searcher = Searcher(self._store, self._embedder)
        self._indexed_docs: dict[str, int] = {}  # nome → chunks

        # Carrega índice existente (se houver)
        self._store.load()

        # Verifica conectividade com o Ollama
        self._ollama_ok = self._check_ollama()

        self._build_ui()
        self.show_all()

    def _check_ollama(self) -> bool:
        """Testa a conexão com o Ollama. Retorna True se OK."""
        try:
            self._embedder.ping()
            return True
        except ConnectionError as exc:
            # Agenda o diálogo de erro para depois que a janela estiver visível
            GLib.idle_add(self._show_ollama_error, str(exc))
            return False

    def _show_ollama_error(self, message: str) -> bool:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Ollama não acessível",
            secondary_text=message,
        )
        dialog.run()
        dialog.destroy()
        return False  # Remove do idle_add

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Header bar
        header = Gtk.HeaderBar()
        header.set_title("Search in Documents")
        header.set_subtitle("Embed Search with Gemma2Embedding")
        header.set_show_close_button(True)

        self.set_titlebar(header)

        # Layout principal: sidebar + painel de busca
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_wide_handle(False)

        self._sidebar = Sidebar(
            on_add_files=self._on_add_files,
            on_clear_index=self._on_clear_index,
        )

        self._search_panel = SearchPanel(on_search=self._on_search)

        paned.pack1(self._sidebar, resize=False, shrink=False)
        paned.pack2(self._search_panel, resize=True, shrink=False)
        paned.set_position(240)

        self.add(paned)

    # ------------------------------------------------------------------
    # Callbacks de indexação
    # ------------------------------------------------------------------

    def _on_add_files(self, paths: list[Path]) -> None:
        """Dispara indexação dos arquivos em thread separada."""
        self._sidebar.set_loading(True)
        self._search_panel.set_status("Indexando documentos…")
        self._search_panel.set_progress(0.0)

        thread = threading.Thread(target=self._index_files_thread, args=(paths,), daemon=True)
        thread.start()

    def _index_files_thread(self, paths: list[Path]) -> None:
        total_files = len(paths)
        for i, path in enumerate(paths):

            def _progress(done: int, total: int, msg: str) -> None:
                fraction = (i + (done / max(total, 1))) / total_files
                GLib.idle_add(self._search_panel.set_progress, fraction, msg)

            try:
                chunks = self._indexer.index_file(path, on_progress=_progress)
                self._indexed_docs[path.name] = chunks
                GLib.idle_add(self._sidebar.add_document_row, path.name, chunks)
            except Exception as exc:
                GLib.idle_add(
                    self._search_panel.set_status,
                    f"Erro: {exc}",
                    "status-error",
                )

        # Salva índice em disco
        self._store.save()

        n_docs = len(self._indexed_docs)
        n_chunks = self._store.total_chunks
        GLib.idle_add(self._sidebar.update_count, n_docs, n_chunks)
        GLib.idle_add(self._search_panel.set_progress, 1.0, "Indexação concluída.")
        GLib.idle_add(self._sidebar.set_loading, False)

    def _on_clear_index(self) -> None:
        self._store.clear()
        self._store.save()
        self._indexed_docs.clear()
        self._sidebar.clear_document_list()
        self._sidebar.update_count(0, 0)
        self._search_panel.clear_results()
        self._search_panel.set_status("Índice limpo.")

    # ------------------------------------------------------------------
    # Callbacks de busca
    # ------------------------------------------------------------------

    def _on_search(self, query: str) -> None:
        """Dispara busca em thread separada."""
        if self._store.total_chunks == 0:
            self._search_panel.set_status(
                "Nenhum documento indexado. Adicione arquivos primeiro.",
                "status-error",
            )
            return

        self._search_panel.set_searching(True)
        thread = threading.Thread(target=self._search_thread, args=(query,), daemon=True)
        thread.start()

    def _search_thread(self, query: str) -> None:
        try:
            results = self._searcher.search(query)
            GLib.idle_add(self._search_panel.show_results, results)
        except Exception as exc:
            GLib.idle_add(self._search_panel.set_status, f"Erro na busca: {exc}", "status-error")
        finally:
            GLib.idle_add(self._search_panel.set_searching, False)
