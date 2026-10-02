
# Import requests.
# We use it to communicate with our FastAPI backend.
import requests

# Import Streamlit.
# Streamlit creates the web interface for our chatbot.
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

# URL of our FastAPI backend.
FASTAPI_URL = "http://127.0.0.1:8000"

# Name of the AI model we are using.
MODEL_NAME = "Qwen3 1.7B"


# =========================================================
# STREAMLIT PAGE CONFIGURATION
# =========================================================

# Configure the browser page.
st.set_page_config(
    page_title="GenAI Chatbot",
    page_icon="🤖",
    layout="centered"
)


# =========================================================
# CUSTOM CSS
# =========================================================

# Add custom CSS to improve the appearance of the chatbot.
st.markdown(
    """
    <style>

    /* Main page title */
    .main-title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    /* Subtitle below the title */
    .subtitle {
        text-align: center;
        color: gray;
        margin-bottom: 25px;
    }

    /* Status box */
    .status-box {
        padding: 10px;
        border-radius: 10px;
        background-color: #f0f2f6;
        text-align: center;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

# Display the main chatbot title.
st.markdown(
    '<div class="main-title">🤖 GenAI Chatbot</div>',
    unsafe_allow_html=True
)

# Display a subtitle.
st.markdown(
    '<div class="subtitle">Powered by Ollama + Qwen3 1.7B</div>',
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

# Streamlit reruns this script whenever the user interacts
# with the page.
#
# session_state allows us to keep information between
# these reruns.

# Check whether our message history already exists.
if "messages" not in st.session_state:

    # Create an empty list for chat messages.
    st.session_state.messages = []


# =========================================================
# SIDEBAR
# =========================================================

# Everything inside this block appears in the sidebar.
with st.sidebar:

    # Sidebar title.
    st.header("⚙️ Chat Settings")

    # Display model information.
    st.write("### 🤖 Model")

    # Show the model name.
    st.info(MODEL_NAME)

    # Display backend information.
    st.write("### 🔌 Backend")

    # Show the backend technology.
    st.info("FastAPI + Ollama")


    # -----------------------------------------------------
    # CHECK BACKEND STATUS
    # -----------------------------------------------------

    # Create a button that checks whether FastAPI is running.
    if st.button("🔄 Check Backend"):

        try:

            # Send a GET request to the FastAPI health endpoint.
            response = requests.get(
                f"{FASTAPI_URL}/health",
                timeout=5
            )

            # Check whether the request was successful.
            response.raise_for_status()

            # Display success message.
            st.success("Backend is connected ✅")

        except requests.exceptions.RequestException:

            # Display an error if FastAPI cannot be reached.
            st.error("Backend is not available ❌")


    # -----------------------------------------------------
    # CLEAR CHAT
    # -----------------------------------------------------

    # Create a button for clearing the conversation.
    if st.button("🗑️ Clear Chat"):

        try:

            # Send a request to FastAPI to clear
            # the backend conversation memory.
            response = requests.post(
                f"{FASTAPI_URL}/memory/clear",
                timeout=5
            )

            # Check whether FastAPI successfully
            # cleared the backend memory.
            response.raise_for_status()

            # Clear the messages displayed in Streamlit.
            st.session_state.messages = []

            # Refresh the Streamlit application.
            st.rerun()

        except requests.exceptions.RequestException as error:

            # Display an error if FastAPI cannot be reached.
            st.error(
                f"Could not clear backend memory: {error}"
            )


    # -----------------------------------------------------
    # PROJECT INFORMATION
    # -----------------------------------------------------

    # Add a separator.
    st.divider()

    # Display project information.
    st.write("### 📌 Project")

    st.write(
        """
        **GenAI Chatbot**

        - Frontend: Streamlit
        - Backend: FastAPI
        - LLM: Qwen3 1.7B
        - Runtime: Ollama
        - Streaming: Enabled
        - Memory: Conversation Memory
        """
    )


# =========================================================
# DISPLAY PREVIOUS MESSAGES
# =========================================================

# Loop through all messages stored in session memory.
for message in st.session_state.messages:

    # Create a chat bubble based on the role.
    #
    # role can be:
    # "user"
    # "assistant"
    with st.chat_message(message["role"]):

        # Display the message content.
        st.markdown(message["content"])


# =========================================================
# USER INPUT
# =========================================================

# Create the chat input box at the bottom.
user_message = st.chat_input(
    "Type your message here..."
)


# =========================================================
# PROCESS USER MESSAGE
# =========================================================

# This block runs when the user sends a message.
if user_message:

    # -----------------------------------------------------
    # DISPLAY USER MESSAGE
    # -----------------------------------------------------

    # Create the user's chat bubble.
    with st.chat_message("user"):

        # Display the user's message.
        st.markdown(user_message)


    # -----------------------------------------------------
    # SAVE USER MESSAGE
    # -----------------------------------------------------

    # Save the user's message in Streamlit memory.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )


    # -----------------------------------------------------
    # AI RESPONSE
    # -----------------------------------------------------

    # Create the assistant's chat bubble.
    with st.chat_message("assistant"):

        # Create an empty area where the response will appear.
        response_placeholder = st.empty()

        # Start with an empty AI response.
        full_response = ""


        # -------------------------------------------------
        # SEND REQUEST TO FASTAPI
        # -------------------------------------------------

        try:

            # Send the user's message to our streaming endpoint.
            response = requests.post(

                # FastAPI streaming endpoint.
                f"{FASTAPI_URL}/chat/stream",

                # Send the message as JSON.
                json={
                    "message": user_message
                },

                # Tell requests to receive the response
                # gradually instead of waiting for everything.
                stream=True,

                # Stop waiting if the server takes too long
                # to respond.
                timeout=120
            )


            # Raise an exception if FastAPI returned an error.
            response.raise_for_status()


            # -------------------------------------------------
            # RECEIVE STREAMING CHUNKS
            # -------------------------------------------------

            # Read the response piece by piece.
            for chunk in response.iter_content(
                chunk_size=None,
                decode_unicode=True
            ):

                # Ignore empty chunks.
                if chunk:

                    # Add the new chunk to the complete response.
                    full_response += chunk

                    # Display the response while it is being generated.
                    #
                    # The "▌" represents a typing cursor.
                    response_placeholder.markdown(
                        full_response + "▌"
                    )


            # -------------------------------------------------
            # FINAL RESPONSE
            # -------------------------------------------------

            # Display the complete response without the cursor.
            response_placeholder.markdown(full_response)


            # -------------------------------------------------
            # SAVE AI RESPONSE
            # -------------------------------------------------

            # Save the complete AI response in session memory.
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )


        # -----------------------------------------------------
        # ERROR HANDLING
        # -----------------------------------------------------

        except requests.exceptions.RequestException as error:

            # Display an error message to the user.
            response_placeholder.error(
                f"Could not connect to the backend: {error}"
            )

