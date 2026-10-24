"""
core/chunker.py
---------------
Divide texto longo em pedaços (chunks) menores com sobreposição opcional.

Estratégia padrão: janela deslizante por palavras.

Uso:
    from core.chunker import chunk_text
    chunks = chunk_text(text, chunk_size=512, overlap=64)
"""

from __future__ import annotations


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 64,
) -> list[str]:
    """Divide *text* em chunks de até *chunk_size* palavras com *overlap* de sobreposição.

    Args:
        text:       Texto de entrada.
        chunk_size: Máximo de palavras por chunk.
        overlap:    Número de palavras compartilhadas entre chunks consecutivos.

    Returns:
        Lista de strings (chunks).
    """
    words = text.split()
    if not words:
        return []

    step = max(1, chunk_size - overlap)
    chunks: list[str] = []

    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(words):
            break

    return chunks
