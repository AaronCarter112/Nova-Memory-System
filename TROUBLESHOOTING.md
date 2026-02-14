# Troubleshooting

## “No response” / empty assistant output
If the frontend expects `data.reply` but the backend returns `content`, update the frontend to read:
- `data.content` (or unify schema)

The `/chat` endpoint returns:
```json
{ "role": "assistant", "content": "..." }
```
fileciteturn1file4

## Qdrant collection missing
On startup, the server creates the collection if it doesn’t exist. fileciteturn1file0  
Make sure Qdrant is reachable at `QDRANT_URL`.

## Ollama not reachable
DSPy is configured to call Ollama on:
- `http://127.0.0.1:11434/v1/` fileciteturn1file9

If Ollama is running elsewhere, change the base URL in `mem/response_generator.py` and `mem/update_memory.py`. fileciteturn1file9 fileciteturn1file10
