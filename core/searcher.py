"""
core/searcher.py
----------------
Realiza busca semântica: embed query → busca no índice → retorna resultados.

Uso:
    from core.searcher import Searcher
    searcher = Searcher(store, embedder)
    results = searcher.search("Como funciona a inflação?", k=5)
"""

from __future__ import annotations

from core.embedder import Embedder
from core.vector_store import SearchResult, VectorStore
from config import config


class Searcher:
    """Busca semântica no índice vetorial."""

    def __init__(
        self,
        store: VectorStore,
        embedder: Embedder,
        top_k: int | None = None,
    ) -> None:
        self.store = store
        self.embedder = embedder
        self.top_k = top_k or config.top_k_results

    def search(self, query: str, k: int | None = None) -> list[SearchResult]:
        """Busca os trechos mais relevantes para *query*.

        Args:
            query: Texto da consulta em linguagem natural.
            k:     Número de resultados (usa top_k se None).

        Returns:
            Lista de SearchResult ordenada por relevância.
        """
        k = k or self.top_k
        query_vector = self.embedder.embed_query(query)
        return self.store.search(query_vector, k=k)
