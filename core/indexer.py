"""
core/indexer.py
---------------
Orquestra o pipeline completo de indexação de um documento:

    parse → chunk → embed → store

Uso:
    from core.indexer import Indexer
    indexer = Indexer(store, embedder)
    indexer.index_file(Path("relatorio.pdf"), on_progress=callback)
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from config import config
from core.chunker import chunk_text
from core.embedder import Embedder
from core.parsers import parse_document
from core.vector_store import VectorStore


ProgressCallback = Callable[[int, int, str], None]
"""Callback de progresso: (chunks_processados, total_chunks, mensagem)."""


class Indexer:
    """Coordena parse → chunk → embed → store para um ou mais arquivos."""

    def __init__(
        self,
        store: VectorStore,
        embedder: Embedder,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self.store = store
        self.embedder = embedder
        self.chunk_size = chunk_size or config.chunk_size
        self.chunk_overlap = chunk_overlap or config.chunk_overlap

    def index_file(
        self,
        path: Path,
        on_progress: ProgressCallback | None = None,
    ) -> int:
        """Indexa um único arquivo.

        Args:
            path:        Caminho para o documento.
            on_progress: Callback opcional de progresso.

        Returns:
            Número de chunks adicionados ao índice.
        """
        # 1. Parse
        if on_progress:
            on_progress(0, 1, f"Lendo {path.name}…")
        text = parse_document(path)

        # 2. Chunk
        chunks = chunk_text(text, self.chunk_size, self.chunk_overlap)
        if not chunks:
            return 0

        total = len(chunks)
        if on_progress:
            on_progress(0, total, f"Gerando embeddings para {path.name}…")

        # 3. Embed (com progresso interno)
        def _embed_progress(done: int, total_: int) -> None:
            if on_progress:
                on_progress(done, total_, f"Embedding {done}/{total_}…")

        vectors = self.embedder.embed_batch(chunks, on_progress=_embed_progress)

        # 4. Metadados
        metadata_list = [
            {
                "doc_path": str(path),
                "doc_name": path.name,
                "chunk_index": i,
                "text": chunk,
            }
            for i, chunk in enumerate(chunks)
        ]

        # 5. Store
        self.store.add(vectors, metadata_list)
        if on_progress:
            on_progress(total, total, f"{path.name} indexado ({total} chunks).")

        return total

    def index_directory(
        self,
        directory: Path,
        recursive: bool = False,
        on_progress: ProgressCallback | None = None,
    ) -> dict[str, int]:
        """Indexa todos os documentos suportados em um diretório.

        Returns:
            Dicionário {nome_arquivo: chunks_adicionados}.
        """
        pattern = "**/*" if recursive else "*"
        files = [
            p
            for p in directory.glob(pattern)
            if p.suffix.lower() in config.supported_extensions
        ]

        results: dict[str, int] = {}
        for path in files:
            try:
                count = self.index_file(path, on_progress=on_progress)
                results[path.name] = count
            except Exception as exc:
                results[path.name] = -1
                if on_progress:
                    on_progress(0, 0, f"Erro em {path.name}: {exc}")

        return results
