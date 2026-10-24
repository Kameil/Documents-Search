"""
utils/logger.py
---------------
Configuração centralizada de logging para o projeto.

Uso:
    from utils.logger import get_logger
    log = get_logger(__name__)
    log.info("Indexando arquivo...")
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

_FORMAT = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=_FORMAT,
    datefmt=_DATE_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_LOG_DIR / "app.log", encoding="utf-8"),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger configurado para o módulo *name*."""
    return logging.getLogger(name)
