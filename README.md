# Nova Memory System (mem0-dspy fork)

A **memory-enabled AI chatbot backend** built on **FastAPI + DSPy + Ollama + Qdrant**.

This repo is a fork/extension of `mem0-dspy`, focused on turning “memory” into a real product feature:
- **automatic long-term memory extraction**
- **semantic retrieval** for personalization
- **memory management commands** (forget/list/search/count/clear)
- **semantic deduplication** to prevent repeated saves

> If you're building a “Nova”-style local assistant that actually remembers things, this project is the backbone.

---

## What Nova does

### Chat flow
The `/chat` endpoint:
1. Detects memory commands (forget/list/search/count/clear) and returns immediately if triggered.  
2. Retrieves relevant memories from Qdrant using semantic search.  
3. Generates a response via DSPy (LiteLLM) pointed at Ollama’s OpenAI-compatible API.  
4. Optionally saves a new memory using a DSPy extraction step.  

(See `main.py` and `mem/response_generator.py`.) fileciteturn1file4 fileciteturn1file9

---

## Features (implemented)

### 1) Long-term memory storage in Qdrant
Memories are stored as vectors + payload:
- `user_id`
- `memory_text`
- `categories` (fixed ontology)
- `date`
- `fact_key` (identity/override key)

The Qdrant collection is created on startup and indexed for `user_id`, `categories`, and `fact_key`. fileciteturn1file2

### 2) Semantic retrieval (meaning-based search)
For each user message, Nova embeds the text and retrieves the top N similar memories. fileciteturn1file9

### 3) Category-based organization
Supported categories:
- `personal_details`
- `user_preferences`
- `projects`
- `routines`
- `meta`
- `general` fileciteturn1file3

### 4) Identity fact updates via `fact_key`
If a memory uses a stable `fact_key` (e.g. `profile.location.current`) it can be treated as a single source of truth. fileciteturn1file10

### 5) Semantic deduplication (for `other.misc`)
When the extracted `fact_key` is `other.misc`, Nova checks for highly similar memories before saving (default 0.90 similarity). fileciteturn1file14 fileciteturn1file6

### 6) Memory management commands
Built-in commands (natural language patterns):
- **Forget**: “forget that I like pizza” (semantic delete, default 0.85) fileciteturn1file5
- **Clear all**: “forget everything” fileciteturn1file5
- **List**: “list my memories” (grouped by category) fileciteturn1file11
- **Search**: “search memories about coffee” fileciteturn1file11
- **Count**: “how many memories do you have?” (with category breakdown) fileciteturn1file11

---

## Architecture

```
FastAPI (main.py)
  └─ /chat
      ├─ memory_commands.detect_memory_command()
      ├─ response_generator.fetch_similar_memories_logic()  -> Qdrant
      ├─ DSPy predictor (NovaResponseSignature)             -> Ollama (/v1)
      └─ update_memory.update_memories()                    -> Qdrant (save)
```

Key modules:
- `main.py` — FastAPI endpoints (`/chat`, plus `/stt` and `/speak` if voice is enabled) fileciteturn1file8
- `mem/response_generator.py` — retrieval + DSPy response signature and LM config fileciteturn1file9
- `mem/update_memory.py` — DSPy-based memory extraction and save + dedup fileciteturn1file14
- `mem/vectordb.py` — Qdrant collection + CRUD + dedup helper fileciteturn1file2
- `mem/memory_commands.py` — command detection + handlers fileciteturn1file1

---

## Requirements

- Python 3.10+ (3.11 recommended)
- **Ollama** running locally
- **Qdrant** running locally (Docker recommended)
- `dspy`, `fastapi`, `uvicorn`, `qdrant-client`, `litellm` (installed via `requirements.txt` / `pyproject.toml` depending on your setup)

---

## Quickstart (local)

### 1) Start Qdrant
```bash
docker run -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

### 2) Start Ollama
Install Ollama and pull a model.
```bash
ollama pull dolphin3
```

Nova uses the OpenAI-compatible API at:
- `http://127.0.0.1:11434/v1/` fileciteturn1file9

### 3) Set environment variables
Create `.env`:

```bash
# Qdrant
QDRANT_URL=http://localhost:6333
EMBEDDING_DIM=768

# Memory thresholds
DUPLICATE_THRESHOLD=0.90
FORGET_THRESHOLD=0.85

# Ollama OpenAI-compatible base
OLLAMA_API_BASE=http://127.0.0.1:11434/v1/
```

### 4) Install and run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 5) Test
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"My name is Aaron"}],"user_id":1}'
```

---

## Memory command cheat sheet

Try these in chat:

- `List my memories`
- `Search memories about coffee`
- `How many memories do you have?`
- `Forget that I like pizza`
- `Forget everything`

Patterns are defined in `mem/memory_commands.py`. fileciteturn1file1

---

## Memory schema

### Payload fields
- `user_id` (int)
- `memory_text` (str)
- `categories` (list[str])
- `date` (str)
- `fact_key` (str, default `other.misc`) fileciteturn1file2

### Category ontology
Defined in `mem/vectordb.py`. fileciteturn1file3

---

## Roadmap (planned)

Short-term:
- Memory editing (update existing memory without deleting)
- Importance levels + re-ranking
- Confirmation prompts for risky/identity changes
- Contradiction detection + user resolution

Medium-term:
- Expiration/TTL memories (time-based + review-based)
- Tags + tag filtering
- Memory versioning + history queries
- Import/export + backup

Long-term:
- Graph relationships between memories
- Clustering + summarization
- Multi-profile / shared memory permissions

---

## Contributing

PRs welcome. Suggested workflow:
1. Fork
2. Create feature branch: `feat/<name>`
3. Add tests (or at least a reproducible curl script)
4. Open PR with before/after behavior

---

## License

Choose one:
- MIT (recommended for maximum reuse), or
- Apache-2.0

If you haven’t chosen yet, add an MIT `LICENSE` file and you’re good.
