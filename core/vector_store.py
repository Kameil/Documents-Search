"""
core/vector_store.py
--------------------
Índice vetorial baseado em FAISS para armazenar e buscar embeddings.

Responsabilidades:
    - Adicionar vetores com metadados associados
    - Persistir / carregar índice em disco
    - Buscar os K vizinhos mais próximos de um vetor de consulta

Estrutura de metadados (por chunk):
    {
        "doc_path": str,       # caminho original do documento
        "doc_name": str,       # nome do arquivo
        "chunk_index": int,    # índice do chunk dentro do documento
        "text": str,           # texto do chunk
    }

Uso:
    from core.vector_store import VectorStore
    store = VectorStore()
    store.add(vectors, metadata_list)
    store.save()
    results = store.search(query_vector, k=5)
"""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from config import config


@dataclass
class SearchResult:
    """Resultado de uma busca semântica."""

    score: float  # distância L2 (menor = mais similar)
    doc_name: str
    doc_path: str
    chunk_index: int
    text: str


class VectorStore:
    """Índice FAISS com metadados persistíveis em disco."""

    def __init__(
        self,
        index_path: Path | None = None,
        metadata_path: Path | None = None,
        dimension: int = 768,  # gemma2embedding default
    ) -> None:
        self.index_path = index_path or config.index_path
        self.metadata_path = metadata_path or config.metadata_path
        self.dimension = dimension

        # Índice FAISS (plano L2)
        self._index: faiss.IndexFlatL2 = faiss.IndexFlatL2(dimension)
        # Lista de metadados paralela ao índice
        self._metadata: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Adição de vetores
    # ------------------------------------------------------------------

    def add(
        self,
        vectors: np.ndarray,
        metadata_list: list[dict[str, Any]],
    ) -> None:
        """Adiciona vetores e seus metadados ao índice.

        Args:
            vectors:       Array (N, D) float32.
            metadata_list: Lista de N dicionários com metadados.
        """
        if vectors.shape[0] != len(metadata_list):
            raise ValueError("vectors e metadata_list devem ter o mesmo tamanho.")

        vectors = np.ascontiguousarray(vectors, dtype=np.float32)
        self._index.add(vectors)
        self._metadata.extend(metadata_list)

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------

    def search(self, query_vector: np.ndarray, k: int = 5) -> list[SearchResult]:
        """Busca os *k* chunks mais similares ao vetor de consulta.

        Args:
            query_vector: Array (D,) ou (1, D) float32.
            k:            Número de resultados.

        Returns:
            Lista de SearchResult ordenada por score crescente.
        """
        if self._index.ntotal == 0:
            return []

        q = np.ascontiguousarray(query_vector.reshape(1, -1), dtype=np.float32)
        k = min(k, self._index.ntotal)
        distances, indices = self._index.search(q, k)

        results: list[SearchResult] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0:
                continue
            meta = self._metadata[idx]
            results.append(
                SearchResult(
                    score=float(dist),
                    doc_name=meta.get("doc_name", ""),
                    doc_path=meta.get("doc_path", ""),
                    chunk_index=meta.get("chunk_index", 0),
                    text=meta.get("text", ""),
                )
            )
        return results

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Salva índice FAISS e metadados em disco."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(self.index_path))
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self._metadata, f)

    def load(self) -> bool:
        """Carrega índice e metadados do disco.

        Returns:
            True se carregado com sucesso, False se arquivos não existem.
        """
        if not self.index_path.exists() or not self.metadata_path.exists():
            return False
        self._index = faiss.read_index(str(self.index_path))
        with open(self.metadata_path, "rb") as f:
            self._metadata = pickle.load(f)
        return True

    def clear(self) -> None:
        """Remove todos os vetores e metadados do índice."""
        self._index.reset()
        self._metadata.clear()

    @property
    def total_chunks(self) -> int:
        """Total de chunks indexados."""
        return self._index.ntotal
