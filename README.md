# Search in Documents

A **semantic search** tool for local documents using **Google Gemini embeddings**, featuring a **PyGTK (GTK 3 / GObject)** graphical interface.

---

## Features

| Feature | Details |
| --- | --- |
| Supported formats | PDF, DOCX, TXT, Markdown, XLSX |
| Embedding model | `models/text-embedding-004` (Gemini) |
| Vector index | FAISS (approximate nearest neighbor search) |
| Chunking | Sliding window with configurable overlap |
| Interface | GTK 3 via PyGObject — dark theme with custom CSS |
| Threading | Indexing and search run in separate threads (UI never freezes) |

---

## Project Structure

```text
search_in_documents/
│
├── main.py                  # Entry point
├── config.py                # Configuration (loads .env)
├── requirements.txt
├── .env.example
│
├── core/                    # Business logic
│   ├── parsers.py           # Text extraction by format
│   ├── chunker.py            # Text splitting into chunks
│   ├── embedder.py           # Google Generative AI wrapper
│   ├── vector_store.py       # FAISS index + persistence
│   ├── indexer.py            # Pipeline: parse → chunk → embed → store
│   └── searcher.py           # Semantic search
│
├── ui/                      # PyGTK interface
│   ├── styles.py             # Global CSS (dark theme)
│   ├── main_window.py        # Main window
│   ├── sidebar.py            # Document list
│   ├── search_panel.py       # Search field + results
│   └── result_card.py        # Individual result card
│
├── utils/
│   └── logger.py             # Centralized logging
│
└── data/                    # Generated at runtime
    └── vector_store/
        ├── faiss.index
        └── metadata.pkl
```

---

## Installation

### 1. Install `uv` (if you haven't already)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. System Dependencies (GTK)

```bash
# Debian / Ubuntu
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Fedora
sudo dnf install python3-gobject gtk3
```

### 3. Create the Environment and Install Python Dependencies

```bash
# Synchronize all dependencies declared in pyproject.toml
uv sync

# Also install development dependencies (pytest, ruff, etc.)
uv sync --dev
```

### 4. Configure Ollama

```bash
# Copy the environment variables template
cp .env.example .env
# Edit .env if Ollama is running on a host other than localhost:11434

# Download the embedding model
ollama pull embeddinggemma-2
```

---

## Usage

```bash
uv run python main.py
```

1. Click **"Add Files"** in the sidebar.
2. Select one or more documents — they will be indexed automatically.
3. Enter a question in the search field and press **Enter** or click **"Search"**.
4. The most relevant passages will appear, ranked by relevance.

---

## Environment Variables (`.env`)

| Variable | Default | Description |
| --- | --- | --- |
| `EMBEDDING_MODEL` | `gemma2embedding` | Embedding model |
| `INDEX_PATH` | `data/vector_store/faiss.index` | FAISS index path |
| `CHUNK_SIZE` | `512` | Words per chunk |
| `CHUNK_OVERLAP` | `64` | Overlapping words between chunks |
| `TOP_K_RESULTS` | `5` | Number of search results returned |

---

## Architecture

```text
┌─────────────┐    parse     ┌──────────┐   chunk   ┌─────────┐
│  Document   │ ──────────▶  │  Parser  │ ────────▶ │ Chunker │
└─────────────┘              └──────────┘           └────┬────┘
                                                         │ chunks
                                                         ▼
                                                   ┌──────────┐
                                                   │ Embedder │ ◀── Ollama Server API (Local)
                                                   └────┬─────┘
                                                        │ vectors
                                                        ▼
                                                  ┌────────────┐
                                                  │ VectorStore│ (FAISS)
                                                  └────┬───────┘
                                                       │
                                    ┌──────────────────┘
                                    │  query vector
                              ┌─────┴──────┐
                 query text ──▶  Searcher  │──▶ SearchResult[]
                              └────────────┘
```
