import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import orchestrator

app = FastAPI(title="Lightweight Local AI Agent API")

class ChatRequest(BaseModel):
    query: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Receives a user query and runs the full agentic pipeline.
    Returns the final answer along with verification and tool traces.
    """
    try:
        result = orchestrator.run_pipeline(req.query)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Serve the frontend
app.mount("/", StaticFiles(directory="web", html=True), name="web")

if __name__ == "__main__":
    print("Starting Lightweight Agent Server at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
