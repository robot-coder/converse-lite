from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import liteLLM
import httpx

app = FastAPI(title="Web-based Chat Assistant")

# Initialize LiteLLM model (assuming a default model; can be extended)
model = liteLLM.LiteLLM()

# In-memory storage for conversation history per session/user
# For simplicity, using a global dict; in production, consider persistent storage
conversation_histories = {}

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    model_name: Optional[str] = None  # Optional model selection

class ChatResponse(BaseModel):
    reply: str
    conversation: List[Message]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Handle chat messages, maintain conversation history, and generate responses.
    """
    try:
        session_id = request.session_id
        user_message = request.message
        model_name = request.model_name

        # Retrieve or initialize conversation history
        history = conversation_histories.get(session_id, [])

        # Append user message to history
        history.append(Message(role="user", content=user_message))

        # Select model if specified
        if model_name:
            # For simplicity, assume model switching is supported
            # In practice, you'd load or switch models accordingly
            # Here, we just log the model selection
            # model = liteLLM.LiteLLM(model_name=model_name)
            pass

        # Generate response from LiteLLM
        # Prepare conversation context
        context = "\n".join([f"{msg.role}: {msg.content}" for msg in history])
        try:
            reply_text = model.chat(context)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model inference error: {str(e)}")

        # Append assistant reply to history
        history.append(Message(role="assistant", content=reply_text))
        conversation_histories[session_id] = history

        return ChatResponse(reply=reply_text, conversation=history)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=dict)
async def upload_media(session_id: str = Form(...), file: UploadFile = File(...)):
    """
    Handle optional multimedia uploads.
    """
    try:
        # Save uploaded file temporarily or process as needed
        content = await file.read()
        # For demonstration, just acknowledge receipt
        # In practice, process or store the media as required
        return {"filename": file.filename, "size": len(content), "message": "Media uploaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)