"""
config.py
---------
Centraliza todas as configurações do projeto.
Carrega variáveis do arquivo .env e expõe constantes tipadas.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Carrega o .env da raiz do projeto
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


@dataclass(frozen=True)
class Config:
    # --- Servidor Ollama ---
    ollama_host: str = field(
        default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )

    # --- Modelo de embedding ---
    embedding_model: str = field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL", "embeddinggemma-2"
        )
    )

    # --- Caminhos ---
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent)
    data_dir: Path = field(
        default_factory=lambda: Path(__file__).parent / "data"
    )
    index_path: Path = field(
        default_factory=lambda: Path(__file__).parent
        / os.getenv("INDEX_PATH", "data/vector_store/faiss.index")
    )
    metadata_path: Path = field(
        default_factory=lambda: Path(__file__).parent
        / "data/vector_store/metadata.pkl"
    )

    # --- Chunking ---
    chunk_size: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "512"))
    )
    chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "64"))
    )

    # --- Busca ---
    top_k_results: int = field(
        default_factory=lambda: int(os.getenv("TOP_K_RESULTS", "5"))
    )

    # --- Extensões suportadas ---
    supported_extensions: tuple[str, ...] = (".pdf", ".docx", ".txt", ".md", ".xlsx")

    def validate(self) -> None:
        """Lança ConnectionError se o Ollama não estiver acessível."""
        import urllib.request
        try:
            urllib.request.urlopen(self.ollama_host, timeout=3)
        except Exception as exc:
            raise ConnectionError(
                f"Ollama não acessível em {self.ollama_host}. "
                f"Certifique-se de que o servidor está rodando. Detalhe: {exc}"
            )


# Instância global (singleton)
config = Config()
