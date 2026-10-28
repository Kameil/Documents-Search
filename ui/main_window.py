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
from dotenv import set_key

gi.require_version("Gtk", "4.0")
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
        self.show()

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
            text="Ollama não acessível",
            secondary_text=message,
        )
        dialog.add_button("OK", Gtk.ResponseType.OK)
        dialog.connect("response", lambda dialog, _response: dialog.destroy())
        dialog.show()
        return False  # Remove do idle_add

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Header bar
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        title = Gtk.Label(label="Search in Documents")
        title.get_style_context().add_class("title")
        subtitle = Gtk.Label(label="Embed Search with Gemma2Embedding")
        subtitle.get_style_context().add_class("subtitle")
        title_box.append(title)
        title_box.append(subtitle)
        header.set_title_widget(title_box)

        settings_button = Gtk.Button(label="⚙")
        settings_button.set_tooltip_text("Configurações")
        settings_button.get_style_context().add_class("btn-toolbar")
        settings_button.connect("clicked", self._on_settings_clicked)
        header.pack_end(settings_button)

        self.set_titlebar(header)

        # Layout principal: sidebar + painel de busca
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_wide_handle(False)

        self._sidebar = Sidebar(
            on_add_files=self._on_add_files,
            on_clear_index=self._on_clear_index,
        )

        self._search_panel = SearchPanel(on_search=self._on_search)

        paned.set_start_child(self._sidebar)
        paned.set_end_child(self._search_panel)
        paned.set_position(240)

        self.set_child(paned)

    # ------------------------------------------------------------------
    # Callbacks de indexação
    # ------------------------------------------------------------------

    def _on_settings_clicked(self, _button: Gtk.Button) -> None:
        """Abre as configurações de conexão e embedding."""
        dialog = Gtk.Dialog(title="Configurações", transient_for=self, modal=True)
        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        dialog.add_button("Salvar", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)

        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(20)
        content.set_margin_end(20)

        description = Gtk.Label(
            label="Escolha o servidor Ollama e o modelo usado para gerar embeddings."
        )
        description.set_halign(Gtk.Align.START)
        description.set_wrap(True)
        content.append(description)

        grid = Gtk.Grid(column_spacing=12, row_spacing=10)
        host_entry = Gtk.Entry(text=self._embedder.host)
        model_entry = Gtk.Entry(text=self._embedder.model)
        host_entry.set_placeholder_text("http://localhost:11434")
        model_entry.set_placeholder_text("embeddinggemma-2")

        for row, (label, entry) in enumerate(
            (("Servidor Ollama", host_entry), ("Modelo de embedding", model_entry))
        ):
            field_label = Gtk.Label(label=label)
            field_label.set_halign(Gtk.Align.END)
            grid.attach(field_label, 0, row, 1, 1)
            entry.set_hexpand(True)
            grid.attach(entry, 1, row, 1, 1)
        content.append(grid)

        dialog.connect("response", self._on_settings_response, host_entry, model_entry)
        dialog.present()

    def _on_settings_response(
        self, dialog: Gtk.Dialog, response: int, host_entry: Gtk.Entry, model_entry: Gtk.Entry
    ) -> None:
        if response == Gtk.ResponseType.OK:
            self._save_settings(host_entry.get_text().strip(), model_entry.get_text().strip())
        dialog.destroy()

    def _save_settings(self, host: str, model: str) -> None:
        if not host or not model:
            self._show_message(
                Gtk.MessageType.ERROR,
                "Configurações inválidas",
                "Informe o servidor Ollama e o modelo de embedding.",
            )
            return

        candidate = Embedder(host=host, model=model)
        try:
            candidate.ping()
        except ConnectionError as exc:
            self._show_message(Gtk.MessageType.ERROR, "Não foi possível aplicar", str(exc))
            return

        if self._store.total_chunks and not self._confirm_model_change():
            return

        env_path = config.base_dir / ".env"
        set_key(str(env_path), "OLLAMA_HOST", host)
        set_key(str(env_path), "EMBEDDING_MODEL", model)

        self._embedder = candidate
        self._indexer = Indexer(self._store, self._embedder)
        self._searcher = Searcher(self._store, self._embedder)

        if self._store.total_chunks:
            self._on_clear_index()
        self._ollama_ok = True
        self._search_panel.set_status(f"Configurações salvas. Modelo ativo: {model}.", "status-success")

    def _confirm_model_change(self) -> bool:
        self._show_message(
            Gtk.MessageType.WARNING,
            "Limpe o índice antes de mudar o modelo",
            "Embeddings de modelos diferentes não podem ser combinados.",
        )
        return False

    def _show_message(self, message_type: Gtk.MessageType, title: str, detail: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=message_type,
            text=title,
            secondary_text=detail,
        )
        dialog.add_button("OK", Gtk.ResponseType.OK)
        dialog.connect("response", lambda dialog, _response: dialog.destroy())
        dialog.show()

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
                progress_message = f"Arquivo {i + 1}/{total_files} · {msg}"
                GLib.idle_add(self._search_panel.set_progress, fraction, progress_message)

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
        GLib.idle_add(
            self._search_panel.set_progress,
            1.0,
            f"Indexação concluída: {total_files} arquivo(s) processado(s).",
        )
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
