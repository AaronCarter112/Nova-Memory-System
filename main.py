"""
Nova AI Backend - Enhanced with memory management commands
"""
from __future__ import annotations

import json
from typing import List, Dict, Optional

import dspy
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from voice import STTEngine, TTSEngine
from mem.response_generator import (
    NovaResponseSignature,
    nova_model,
    fetch_similar_memories_logic,
)
from mem.update_memory import update_memories
from mem.vectordb import create_memory_collection, client as qdrant_client
from mem.memory_commands import detect_memory_command

app = FastAPI(title="Nova AI Backend")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for /chat endpoint"""
    messages: List[Dict[str, str]]
    user_id: Optional[int] = 1


# Initialize STT and TTS engines
stt_engine = STTEngine()
tts_engine = TTSEngine()


@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    try:
        # Create Qdrant collection if it doesn't exist
        await create_memory_collection()
        print("✅ Nova Neural Core & Vector DB Ready.")
        print("📡 Ollama endpoint: http://127.0.0.1:11434/v1/")
        print("🤖 Model: openai/Dolphin3:latest (via LiteLLM)")
        print("💾 Memory Commands: forget, list, search, count, clear")
        
    except Exception as e:
        print(f"❌ STARTUP ERROR: {e}")
        import traceback
        traceback.print_exc()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    try:
        # Close Qdrant client to avoid unclosed session warnings
        await qdrant_client.close()
        print("🧹 Qdrant client session closed.")
    except Exception as e:
        print(f"❌ QDRANT SHUTDOWN ERROR: {e}")


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Main chat endpoint that:
    1. Checks for memory management commands
    2. Retrieves relevant memories from Qdrant
    3. Generates a response using DSPy + Ollama
    4. Optionally saves new memories
    
    Returns:
        JSON with role="assistant" and content containing the response
    """
    try:
        # Validate input
        if not req.messages:
            raise HTTPException(status_code=400, detail="No messages provided.")

        user_id = req.user_id or 1
        user_input = req.messages[-1]["content"]
        
        if not user_input or not user_input.strip():
            raise HTTPException(status_code=400, detail="Empty message content.")

        print(f"\n{'='*60}")
        print(f"👤 USER [{user_id}]: {user_input}")
        print(f"{'='*60}")

        # Step 0: Check for memory management commands
        is_command, command_response = await detect_memory_command(user_input, user_id)
        
        if is_command:
            print(f"🎮 MEMORY COMMAND DETECTED")
            print(f"📋 Response: {command_response[:100]}...")
            
            # Return command response directly
            return {
                "role": "assistant",
                "content": command_response
            }

        # Step 1: Retrieve relevant memories
        print("🔍 Fetching memories...")
        memories = await fetch_similar_memories_logic(
            search_text=user_input,
            user_id=user_id,
            limit=3,
        )
        print(f"📚 Found {len(memories)} relevant memories")

        # Step 2: Generate response using DSPy
        print("🤖 Generating response...")
        predictor = dspy.Predict(NovaResponseSignature)

        # Set nova_model as the LM for this prediction
        with dspy.context(lm=nova_model):
            out = await predictor.acall(
                transcript=req.messages[:-1],  # All messages except the current one
                memories=memories,
                question=user_input,
            )

        response_text = (out.response or "").strip()
        
        if not response_text:
            # Fallback if model returns empty response
            response_text = "I'm having trouble formulating a response right now. Could you rephrase that?"

        print(f"🤖 NOVA: {response_text}")

        # Step 3: Save new memory if needed
        should_save = bool(getattr(out, "save_memory", False))
        print(f"💾 Save memory: {should_save}")
        
        if should_save:
            # Build full conversation history including this response
            full_history = req.messages + [
                {"role": "assistant", "content": response_text}
            ]
            
            # Use last 4-6 messages as context for memory extraction
            context_messages = full_history[-6:]
            
            print("💾 Attempting to save memory...")
            memory_saved = await update_memories(
                user_id=user_id,
                messages=context_messages
            )
            
            if memory_saved:
                print("✅ Memory saved successfully")
            else:
                print("ℹ️  No memory was saved (duplicate or no new info)")

        # Step 4: Prepare response
        # Optionally attach top memory for UI visualization
        final_content = response_text
        if memories:
            # Add the top memory as JSON for frontend to parse
            final_content += f"\n{json.dumps(memories[0])}"

        return {
            "role": "assistant",
            "content": final_content
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        print(f"❌ CHAT ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a safe error message
        error_response = (
            "I encountered an error while processing your message. "
            "Please check that Ollama is running with the Dolphin3 model loaded."
        )
        
        return {
            "role": "assistant",
            "content": error_response
        }


@app.post("/speak")
async def speak(req: dict):
    """
    TTS endpoint - converts text to speech
    
    Args:
        req: dict with 'text' key
        
    Returns:
        Status of TTS operation
    """
    try:
        text = (req.get("text") or "").strip()
        
        if not text:
            return {"status": "no_text"}
        
        # Call TTS engine
        tts_engine.speak(text)
        return {"status": "ok"}
        
    except Exception as e:
        print(f"❌ SPEAK ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    """
    STT endpoint - converts audio to text
    
    Args:
        file: Audio file upload
        
    Returns:
        Transcribed text
    """
    try:
        # Read audio bytes
        audio_bytes = await file.read()
        
        # Transcribe
        text = stt_engine.transcribe_bytes(audio_bytes)
        
        return {"text": text}
        
    except Exception as e:
        print(f"❌ STT ERROR: {e}")
        return {"error": str(e), "text": ""}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Nova AI Backend",
        "ollama_endpoint": "http://127.0.0.1:11434/v1/",
        "model": "openai/Dolphin3:latest",
        "features": [
            "chat",
            "memory_save",
            "memory_forget",
            "memory_list",
            "memory_search",
            "memory_count",
            "stt",
            "tts"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
