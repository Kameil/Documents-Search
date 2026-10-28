"""
core/embedder.py
----------------
Wrapper sobre o cliente oficial `ollama` para gerar embeddings de texto
usando o modelo **embeddinggemma-2** (ou qualquer outro configurado).

O servidor Ollama deve estar rodando localmente (padrão: http://localhost:11434).
Para baixar o modelo:
    ollama pull embeddinggemma-2

API do SDK:
    response = ollama.embed(model="embeddinggemma-2", input="texto")
    # response.embeddings → list[list[float]]

Uso:
    from core.embedder import Embedder
    embedder = Embedder()
    vector  = embedder.embed("Olá mundo")
    vectors = embedder.embed_batch(["texto 1", "texto 2"])
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
import ollama

from config import config


class Embedder:
    """Gera embeddings via Ollama usando o modelo embeddinggemma-2."""

    def __init__(self, host: str | None = None, model: str | None = None) -> None:
        # Cria um cliente apontando para o host configurado
        self.host = host or config.ollama_host
        self.model = model or config.embedding_model
        self._client = ollama.Client(host=self.host)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def embed(self, text: str) -> np.ndarray:
        """Gera um embedding para um único texto.

        Args:
            text: Texto de entrada.

        Returns:
            Array numpy float32 com o vetor de embedding.
        """
        response = self._client.embed(model=self.model, input=text)
        # response.embeddings é list[list[float]] mesmo para 1 input
        return np.array(response.embeddings[0], dtype=np.float32)

    def embed_batch(
        self,
        texts: Sequence[str],
        on_progress: Callable[[int, int], None] | None = None,
    ) -> np.ndarray:
        """Gera embeddings para uma lista de textos.

        A API do Ollama aceita uma lista de strings diretamente em `input`,
        retornando todos os vetores em uma única chamada.

        Args:
            texts:       Lista de textos.
            on_progress: Callback opcional (idx_atual, total) para progresso.

        Returns:
            Array numpy (N, D) onde N = len(texts) e D = dimensão do embedding.
        """
        texts = list(texts)
        total = len(texts)

        if on_progress:
            on_progress(0, total)

        response = self._client.embed(model=self.model, input=texts)
        vectors = [np.array(v, dtype=np.float32) for v in response.embeddings]

        if on_progress:
            on_progress(total, total)

        return np.stack(vectors)

    def embed_query(self, query: str) -> np.ndarray:
        """Atalho semântico para gerar embedding de uma consulta.

        Internamente idêntico a `embed()` — o embeddinggemma-2 não exige
        task_type separado; a distinção document/query é transparente.
        """
        return self.embed(query)

    # ------------------------------------------------------------------
    # Utilitário de diagnóstico
    # ------------------------------------------------------------------

    def ping(self) -> bool:
        """Verifica se o servidor Ollama está acessível e o modelo disponível.

        Returns:
            True se o servidor respondeu com sucesso.

        Raises:
            ConnectionError: se o servidor não estiver acessível.
        """
        try:
            # Testa com texto mínimo
            self._client.embed(model=self.model, input="ping")
            return True
        except Exception as exc:
            raise ConnectionError(
                f"Falha ao conectar ao Ollama ({self.host}) "
                f"com o modelo '{self.model}'. "
                f"Execute: ollama pull {self.model}\nDetalhe: {exc}"
            ) from exc
