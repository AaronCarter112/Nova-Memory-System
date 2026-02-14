# Architecture

This project is a memory-enabled chatbot backend.

## Core flow

The `/chat` endpoint:

1. **Memory command detection**  
   If the user asks to list/search/forget/count/clear memories, the server returns immediately with the command result. fileciteturn1file4

2. **Memory retrieval**  
   The user message is embedded and used to query Qdrant for similar memories. fileciteturn1file9

3. **Response generation**  
   DSPy runs `NovaResponseSignature` using a LiteLLM-backed LM pointing to Ollama’s OpenAI-compatible API. fileciteturn1file9

4. **Memory extraction + save**  
   If the response sets `save_memory=True`, Nova extracts a stable memory statement and saves it to Qdrant, applying semantic deduplication for `other.misc`. fileciteturn1file8 fileciteturn1file14

---

## Modules

- `main.py`  
  FastAPI server, endpoints, startup/shutdown hooks, and chat pipeline. fileciteturn1file0

- `mem/response_generator.py`  
  - LM config pointing to Ollama `/v1`  
  - Memory retrieval helper `fetch_similar_memories_logic()`  
  - DSPy signature `NovaResponseSignature` fileciteturn1file9

- `mem/update_memory.py`  
  - DSPy signature `UpdateMemorySignature`  
  - `update_memories()` which extracts + embeds + stores memories  
  - Semantic dedup logic for `other.misc` fileciteturn1file14

- `mem/vectordb.py`  
  Qdrant client, collection setup, indexes, insert/search/list/delete helpers. fileciteturn1file2

- `mem/memory_commands.py`  
  Natural language command patterns and command handlers. fileciteturn1file1
