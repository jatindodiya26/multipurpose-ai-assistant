from fastapi import FastAPI
from pydantic import BaseModel

from agent import run_agent

from auth import (
    register_user,
    login_user
)

from database import (
    save_message,
    get_chat_history,
    create_chat_session,
    get_chat_sessions,
    get_chat_session,
    update_chat_session_title,
    delete_chat_session
)

class SessionRequest(BaseModel):
     
    user_id: int

class SessionTitleRequest(BaseModel):
     
    user_id: int
    title: str

app = FastAPI(
    title="Multipurpose AI Assistant API",
    description="Backend API for the Multipurpose AI Assistant",
    version="1.0.0"
)


# --------------------------------------------------
# Request Models
# --------------------------------------------------
class RegisterRequest(BaseModel):
     
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):

    email: str
    password: str

class ChatRequest(BaseModel):
     
    message: str
    session_id: str
    user_id: int


class ChatResponse(BaseModel):

    response: str


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Multipurpose AI Assistant API is running!"
    }

# --------------------------------------------------
# Register Endpoint
# --------------------------------------------------

@app.post("/register")
def register(request: RegisterRequest):

    success, message = register_user(
        request.username,
        request.email,
        request.password
    )

    return {
        "success": success,
        "message": message
    }

# --------------------------------------------------
# Login Endpoint
# --------------------------------------------------

@app.post("/login")
def login(request: LoginRequest):

    success, user, message = login_user(
        request.email,
        request.password
    )

    if not success:

        return {
            "success": False,
            "message": message
        }

    return {
        "success": True,
        "message": message,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    }

# --------------------------------------------------
# Create Chat Session
# --------------------------------------------------

@app.post("/sessions")
def create_session(
    request: SessionRequest
):

    session_id = create_chat_session(
        request.user_id
    )

    return {
        "success": True,
        "session_id": session_id,
        "title": "New Chat"
    }

# --------------------------------------------------
# Rename Chat Session
# --------------------------------------------------

@app.patch("/sessions/{session_id}")
def rename_session(
    session_id: int,
    request: SessionTitleRequest
):

    title = request.title.strip()

    if not title:

        return {
            "success": False,
            "message": "Title cannot be empty."
        }

    if len(title) > 200:

        return {
            "success": False,
            "message": "Title is too long."
        }

    success = update_chat_session_title(
        session_id,
        request.user_id,
        title
    )

    if not success:

        return {
            "success": False,
            "message": "Session not found."
        }

    return {
        "success": True,
        "message": "Chat renamed successfully."
    }

# --------------------------------------------------
# Delete Chat Session
# --------------------------------------------------

@app.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    user_id: int
):

    success = delete_chat_session(
        session_id,
        user_id
    )

    if not success:

        return {
            "success": False,
            "message": "Session not found."
        }

    return {
        "success": True,
        "message": "Chat deleted successfully."
    }
# --------------------------------------------------
# Get User Chat Sessions
# --------------------------------------------------

@app.get("/sessions/{user_id}")
def sessions(user_id: int):

    return {
        "sessions": get_chat_sessions(
            user_id
        )
    }

# --------------------------------------------------
# Get Session History
# --------------------------------------------------

@app.get("/sessions/{session_id}/history/{user_id}")
def session_history(
    session_id: int,
    user_id: int
):

    session = get_chat_session(
        session_id,
        user_id
    )

    if not session:

        return {
            "success": False,
            "messages": []
        }

    return {
        "success": True,
        "messages": get_chat_history(
            str(session_id)
        )
    }
# --------------------------------------------------
# Get Chat History
# --------------------------------------------------

@app.get("/history/{session_id}")
def history(session_id: str):

    return {
        "messages": get_chat_history(session_id)
    }


# --------------------------------------------------
# Chat Endpoint
# --------------------------------------------------

# --------------------------------------------------
# Chat Endpoint
# --------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    # --------------------------------------------------
    # Verify session ownership
    # --------------------------------------------------

    session = get_chat_session(
        int(request.session_id),
        request.user_id
    )

    if not session:

        return {
            "response": (
                "❌ This chat session does not "
                "belong to the current user."
            )
        }


    # --------------------------------------------------
    # Get previous conversation
    # --------------------------------------------------

    chat_history = get_chat_history(
        request.session_id
    )


    # --------------------------------------------------
    # Generate AI response
    # --------------------------------------------------

    response = run_agent(
    user_input=request.message,
    chat_history=chat_history,
    user_id=request.user_id
)


    # --------------------------------------------------
    # Save user message
    # --------------------------------------------------

    save_message(
        request.session_id,
        "user",
        request.message
    )


    # --------------------------------------------------
    # Save assistant response
    # --------------------------------------------------

    save_message(
        request.session_id,
        "assistant",
        response
    )


    # --------------------------------------------------
    # Automatically generate title
    # --------------------------------------------------

    if session["title"] == "New Chat":

        title = request.message.strip()

        if len(title) > 40:

            title = title[:40].strip() + "..."

        if not title:

            title = "New Chat"

        update_chat_session_title(
            int(request.session_id),
            request.user_id,
            title
        )


    return {
        "response": response
    }