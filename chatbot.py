import json
import requests

# Import our SQLite database functions.
from app.database import (
    init_db,
    save_message,
    load_messages,
    clear_messages,
)


# ============================================================
# Ollama Configuration
# ============================================================

# URL of the Ollama chat API.
OLLAMA_URL = "http://localhost:11434/api/chat"

# Ollama model we are using.
MODEL = "qwen3:1.7b"


# ============================================================
# System Message
# ============================================================

# Instructions given to the AI at the beginning of the conversation.
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a helpful and friendly AI assistant. "
        "Remember important information from the conversation "
        "and use it when answering future questions. "
        "If the user tells you their name, remember it and use it naturally. "
        "Do not claim that you are the user or have the user's identity."
    ),
}


# ============================================================
# Initialize Database
# ============================================================

# Create the database and messages table if they don't exist.
init_db()


# ============================================================
# Conversation Memory
# ============================================================

# Start with the system message.
conversation_history = [SYSTEM_MESSAGE]

# Load previous messages from SQLite.
saved_messages = load_messages()

# Add saved messages to the current conversation.
conversation_history.extend(saved_messages)


# ============================================================
# Normal Chat Function
# ============================================================

def chat(user_message):
    """
    Send a complete message to Ollama and return
    the complete AI response.
    """

    # Add the user's message to the current conversation.
    conversation_history.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # Save the user's message permanently in SQLite.
    save_message("user", user_message)

    # Prepare the request for Ollama.
    payload = {
        "model": MODEL,
        "messages": conversation_history,
        "stream": False,
    }

    # Send request to Ollama.
    response = requests.post(
        OLLAMA_URL,
        json=payload,
    )

    # Raise an error if Ollama returns an error.
    response.raise_for_status()

    # Convert response into Python dictionary.
    data = response.json()

    # Extract AI response.
    assistant_response = data["message"]["content"]

    # Save AI response to current conversation memory.
    conversation_history.append(
        {
            "role": "assistant",
            "content": assistant_response,
        }
    )

    # Save AI response permanently in SQLite.
    save_message("assistant", assistant_response)

    # Return complete response.
    return assistant_response


# ============================================================
# Streaming Chat Function
# ============================================================

def chat_stream(user_message):
    """
    Send a message to Ollama and stream the AI response
    piece by piece.
    """

    # Add user's message to conversation memory.
    conversation_history.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # Save user's message permanently in SQLite.
    save_message("user", user_message)

    # Prepare request for Ollama.
    payload = {
        "model": MODEL,
        "messages": conversation_history,
        "stream": True,
    }

    # Send request to Ollama.
    response = requests.post(
        OLLAMA_URL,
        json=payload,
        stream=True,
    )

    # Stop if Ollama returns an error.
    response.raise_for_status()

    # Store the complete AI response.
    assistant_response = ""

    # Read Ollama's streaming response.
    for line in response.iter_lines():

        # Ignore empty lines.
        if not line:
            continue

        # Convert bytes into text.
        data = line.decode("utf-8")

        # Convert JSON text into Python dictionary.
        chunk = json.loads(data)

        # Extract generated text.
        text = chunk.get("message", {}).get("content", "")

        # Add the text to the complete AI response.
        assistant_response += text

        # Send this piece to Streamlit.
        yield text

    # After streaming is finished,
    # add the complete AI response to memory.
    conversation_history.append(
        {
            "role": "assistant",
            "content": assistant_response,
        }
    )

    # Save the complete AI response permanently in SQLite.
    save_message("assistant", assistant_response)


# ============================================================
# Clear Conversation Memory
# ============================================================

def clear_memory():
    """
    Delete the current conversation and start fresh.
    """

    # Remove messages from the Python memory.
    conversation_history.clear()

    # Add the system message again.
    conversation_history.append(SYSTEM_MESSAGE)

    # Delete messages from SQLite.
    clear_messages()