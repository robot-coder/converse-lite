# README.md

# Web-Based Chat Assistant

This project implements a web-based conversational AI assistant with a front-end JavaScript UI and a back-end Python FastAPI server. The server interacts with LiteLLM to provide AI responses, supporting features such as model selection, conversation history, and optional multimedia uploads.

## Features

- Select different language models
- Maintain conversation history
- Upload multimedia files (images, audio, etc.)
- Real-time chat interface

## Technologies Used

- FastAPI for the backend API
- Uvicorn as the ASGI server
- LiteLLM for language model inference
- Pydantic for data validation
- Starlette for static files and middleware
- HTTPX for HTTP requests (if needed)
- JavaScript for the front-end UI (not included in this repo)

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

---

## API Endpoints

- `GET /models` - List available models
- `POST /chat` - Send a message and receive a response
- `POST /upload` - Upload multimedia files
- `GET /history` - Retrieve conversation history

---

## Front-End Integration

The front-end UI should interact with these endpoints via JavaScript fetch/AJAX calls. (Implementation of the front-end is outside the scope of this README.)

---

## Files

- `main.py` - FastAPI server implementation
- `requirements.txt` - Dependencies list
- `README.md` - This documentation

---

## License

This project is licensed under the MIT License.

---

## Contact

For questions or support, please open an issue or contact [Your Name] at [your.email@example.com].

---

# requirements.txt

fastapi
uvicorn
liteLLM
pydantic
starlette
httpx

---

# main.py

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import liteLLM
import os

app = FastAPI()

# Initialize LiteLLM model (assuming a default model)
model = liteLLM.load_model("default-model")

# Store conversation history in-memory (for demo purposes)
conversation_histories = {}

class Message(BaseModel):
    user_id: str
    message: str
    model_name: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str

@app.get("/models")
async def get_models() -> List[str]:
    """
    Return a list of available LiteLLM models.
    """
    try:
        models = liteLLM.list_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(msg: Message):
    """
    Handle chat messages, maintain conversation history, and return AI responses.
    """
    user_id = msg.user_id
    user_message = msg.message
    model_name = msg.model_name or "default-model"

    # Initialize conversation history if not present
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    # Append user message to history
    conversation_histories[user_id].append({"role": "user", "content": user_message})

    try:
        # Generate response from LiteLLM
        response = liteLLM.chat(
            model_name=model_name,
            messages=conversation_histories[user_id]
        )
        reply_text = response.get("reply", "")

        # Append assistant reply to history
        conversation_histories[user_id].append({"role": "assistant", "content": reply_text})

        return ChatResponse(reply=reply_text, conversation_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_media(file: UploadFile = File(...)):
    """
    Handle multimedia file uploads.
    """
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_location = os.path.join(upload_dir, file.filename)
        with open(file_location, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return {"filename": file.filename, "status": "uploaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    """
    Retrieve conversation history for a user.
    """
    history = conversation_histories.get(user_id, [])
    return {"conversation": history}