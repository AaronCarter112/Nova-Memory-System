# Configuration

Nova uses environment variables for Qdrant and memory behavior.

## Vector DB
- `QDRANT_URL` (default: `http://localhost:6333`) fileciteturn1file3
- `EMBEDDING_DIM` (default: 768) fileciteturn1file3
- `QDRANT_HOST` / `QDRANT_PORT` (optional alternative to QDRANT_URL) fileciteturn1file3

## Memory thresholds
- `DUPLICATE_THRESHOLD` (default: 0.90) fileciteturn1file3
- `FORGET_THRESHOLD` (recommended: 0.85)

## Ollama / LiteLLM base
This project points DSPy’s LM to Ollama’s OpenAI-compatible endpoint:
- `http://127.0.0.1:11434/v1/` fileciteturn1file9

(If you refactor, expose this as an env var like `OLLAMA_API_BASE`.)
