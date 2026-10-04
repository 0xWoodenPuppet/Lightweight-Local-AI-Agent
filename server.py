import uuid
from typing import Optional
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent.memory import process_memory
from agent.orchestrator import run_pipeline
from agent.storage import (
    list_conversations,
    get_conversation,
    save_conversation,
    delete_conversation,
)

app = FastAPI(title="Lightweight Local AI Agent API")


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None


@app.get("/api/conversations")
async def get_conversations():
    """List all saved conversations from local SQLite disk storage, newest first."""
    try:
        convs = list_conversations()
        return JSONResponse(content=convs)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/conversations/{conv_id}")
async def get_single_conversation(conv_id: str):
    """Retrieve full transcript and metadata for a single conversation."""
    try:
        conv = get_conversation(conv_id)
        if not conv:
            return JSONResponse(content={"error": "Conversation not found"}, status_code=404)
        return JSONResponse(content=conv)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.delete("/api/conversations/{conv_id}")
async def remove_conversation(conv_id: str):
    """Delete a conversation from local SQLite storage."""
    try:
        success = delete_conversation(conv_id)
        return JSONResponse(content={"success": success})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Receives a user query, processes compacted memory, runs pipeline,
    and records full transcript to local disk storage.
    """
    try:
        conv_id = req.conversation_id or str(uuid.uuid4())
        conv = get_conversation(conv_id)

        if conv:
            messages = conv.get("messages", [])
            title = conv.get("title", req.query[:50])
            summary = conv.get("summary", "")
            summarized_count = conv.get("summarized_count", 0)
        else:
            messages = []
            title = req.query[:50].strip() or "New conversation"
            summary = ""
            summarized_count = 0

        # Compact memory: get verbatim sliding window (last 6 messages) and updated summary
        verbatim_history, active_summary, updated_count = process_memory(
            messages, summary, summarized_count
        )

        # Run pipeline with compacted memory (router classifies on current query alone)
        result = run_pipeline(
            req.query,
            verbatim_history=verbatim_history,
            memory_summary=active_summary
        )

        # Record user message in transcript
        messages.append({
            "role": "user",
            "content": req.query
        })

        # Record assistant response with full transcript attributes
        messages.append({
            "role": "assistant",
            "content": result.get("final_answer", ""),
            "chosen_skill": result.get("chosen_skill", "none"),
            "skill_input": result.get("skill_input", ""),
            "skill_output": result.get("skill_output", ""),
            "verification": result.get("verification", None),
        })

        # Save to SQLite disk storage with updated summary and count
        save_conversation(conv_id, title, messages, active_summary, updated_count)

        # Attach conversation metadata to response
        result["conversation_id"] = conv_id
        result["title"] = title
        result["summary"] = active_summary
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Serve the frontend
app.mount("/", StaticFiles(directory="web", html=True), name="web")

if __name__ == "__main__":
    print("Starting Lightweight Agent Server at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
