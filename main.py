from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.chatbot import chat, chat_stream, clear_memory


app = FastAPI(
    title="GenAI Chatbot API",
    description="API for our local Ollama chatbot",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "GenAI Chatbot API is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    answer = chat(request.message)

    return {
        "answer": answer
    }


@app.post("/chat/stream")
def chat_stream_endpoint(request: ChatRequest):

    return StreamingResponse(
        chat_stream(request.message),
        media_type="text/plain"
    )
@app.post("/memory/clear")
def clear_memory_endpoint():

    # Clear the conversation memory in the chatbot.
    clear_memory()

    return {
        "message": "Conversation memory cleared successfully."
    }