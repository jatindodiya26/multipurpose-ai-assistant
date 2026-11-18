import os

import requests
import streamlit as st

from rag import (
    add_pdf_to_vectorstore,
    delete_pdf,
    get_user_pdfs
)

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Multipurpose AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# ==================================================
# API CONFIGURATION
# ==================================================

API_URL = "http://127.0.0.1:8000"


# ==================================================
# INITIALIZE SESSION STATE
# ==================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []


# ==================================================
# AUTHENTICATION PAGE
# ==================================================

if not st.session_state.logged_in:

    st.title("🤖 Multipurpose AI Assistant")

    st.caption(
        "AI Assistant with RAG, Tools, Web Search and Persistent Memory"
    )

    st.divider()

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )


    # ==================================================
    # LOGIN
    # ==================================================

    with login_tab:

        st.subheader("Login")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )


        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Please enter both email and password."
                )

            else:

                try:

                    response = requests.post(
                        f"{API_URL}/login",
                        json={
                            "email": email,
                            "password": password
                        },
                        timeout=10
                    )

                    response.raise_for_status()

                    data = response.json()


                    if data.get("success"):

                        user = data["user"]

                        st.session_state.logged_in = True

                        st.session_state.user = user


                        # ------------------------------------------
                        # Load existing sessions
                        # ------------------------------------------

                        sessions_response = requests.get(
                            f"{API_URL}/sessions/"
                            f"{user['id']}",
                            timeout=10
                        )

                        sessions_response.raise_for_status()

                        sessions = (
                            sessions_response
                            .json()
                            .get("sessions", [])
                        )

                        st.session_state.chat_sessions = sessions


                        # ------------------------------------------
                        # Create first session if none exists
                        # ------------------------------------------

                        if not sessions:

                            create_response = requests.post(
                                f"{API_URL}/sessions",
                                json={
                                    "user_id": user["id"]
                                },
                                timeout=10
                            )

                            create_response.raise_for_status()

                            new_session = (
                                create_response
                                .json()
                            )

                            session_id = new_session[
                                "session_id"
                            ]

                            st.session_state.active_session_id = (
                                session_id
                            )


                            # Reload sessions

                            sessions_response = requests.get(
                                f"{API_URL}/sessions/"
                                f"{user['id']}",
                                timeout=10
                            )

                            sessions_response.raise_for_status()

                            st.session_state.chat_sessions = (
                                sessions_response
                                .json()
                                .get("sessions", [])
                            )

                        else:

                            # Open most recently updated chat

                            st.session_state.active_session_id = (
                                sessions[0]["id"]
                            )


                        # ------------------------------------------
                        # Load active chat history
                        # ------------------------------------------

                        active_session_id = (
                            st.session_state.active_session_id
                        )

                        history_response = requests.get(
                            f"{API_URL}/sessions/"
                            f"{active_session_id}/history/"
                            f"{user['id']}",
                            timeout=10
                        )

                        history_response.raise_for_status()

                        history_data = (
                            history_response
                            .json()
                        )

                        st.session_state.messages = (
                            history_data
                            .get("messages", [])
                        )


                        st.success(
                            f"Welcome back, "
                            f"{user['username']}! 👋"
                        )

                        st.rerun()


                    else:

                        st.error(
                            data.get(
                                "message",
                                "Login failed."
                            )
                        )


                except requests.exceptions.ConnectionError:

                    st.error(
                        "❌ Could not connect to FastAPI."
                    )


                except requests.exceptions.Timeout:

                    st.error(
                        "❌ Login request timed out."
                    )


                except Exception as e:

                    st.error(
                        f"❌ Something went wrong: {str(e)}"
                    )


    # ==================================================
    # REGISTER
    # ==================================================

    with register_tab:

        st.subheader("Create Account")

        username = st.text_input(
            "Username",
            key="register_username"
        )

        register_email = st.text_input(
            "Email",
            key="register_email"
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )


        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if (
                not username
                or not register_email
                or not register_password
            ):

                st.error(
                    "Please fill in all fields."
                )

            elif register_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(register_password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                try:

                    response = requests.post(
                        f"{API_URL}/register",
                        json={
                            "username": username,
                            "email": register_email,
                            "password": register_password
                        },
                        timeout=10
                    )

                    response.raise_for_status()

                    data = response.json()


                    if data.get("success"):

                        st.success(
                            "Account created successfully! "
                            "You can now log in. ✅"
                        )

                    else:

                        st.error(
                            data.get(
                                "message",
                                "Registration failed."
                            )
                        )


                except requests.exceptions.ConnectionError:

                    st.error(
                        "❌ Could not connect to FastAPI."
                    )


                except requests.exceptions.Timeout:

                    st.error(
                        "❌ Registration request timed out."
                    )


                except Exception as e:

                    st.error(
                        f"❌ Something went wrong: {str(e)}"
                    )


    st.stop()


# ==================================================
# AUTHENTICATED APPLICATION
# ==================================================

st.title("🤖 Multipurpose AI Assistant")

st.caption(
    "Powered by LangChain + Groq + RAG + AI Tools"
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    # ==================================================
    # ACCOUNT
    # ==================================================

    st.header("👤 Account")

    st.write(
        f"**Username:** "
        f"{st.session_state.user['username']}"
    )

    st.write(
        f"**Email:** "
        f"{st.session_state.user['email']}"
    )


    # ==================================================
    # LOGOUT
    # ==================================================

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.user = None

        st.session_state.active_session_id = None

        st.session_state.messages = []

        st.session_state.chat_sessions = []

        st.rerun()


    st.divider()


    # ==================================================
    # CONVERSATIONS
    # ==================================================

    st.header("💬 Conversations")


    # ==================================================
    # NEW CHAT
    # ==================================================

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        try:

            response = requests.post(
                f"{API_URL}/sessions",
                json={
                    "user_id": (
                        st.session_state.user["id"]
                    )
                },
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            new_session_id = data["session_id"]

            st.session_state.active_session_id = (
                new_session_id
            )

            st.session_state.messages = []


            # Reload sessions

            sessions_response = requests.get(
                f"{API_URL}/sessions/"
                f"{st.session_state.user['id']}",
                timeout=10
            )

            sessions_response.raise_for_status()

            st.session_state.chat_sessions = (
                sessions_response
                .json()
                .get("sessions", [])
            )

            st.rerun()


        except Exception as e:

            st.error(
                f"Unable to create new chat: {str(e)}"
            )


    # ==================================================
    # EXISTING SESSIONS
    # ==================================================

    for chat_session in st.session_state.chat_sessions:

        session_id = chat_session["id"]

        title = chat_session.get(
            "title",
            "New Chat"
        )

        button_label = f"💬 {title}"


        if st.button(
            button_label,
            key=f"session_{session_id}",
            use_container_width=True
        ):

            try:

                history_response = requests.get(
                    f"{API_URL}/sessions/"
                    f"{session_id}/history/"
                    f"{st.session_state.user['id']}",
                    timeout=10
                )

                history_response.raise_for_status()

                history_data = (
                    history_response
                    .json()
                )


                if history_data.get("success"):

                    st.session_state.active_session_id = (
                        session_id
                    )

                    st.session_state.messages = (
                        history_data
                        .get("messages", [])
                    )

                    st.rerun()


                else:

                    st.error(
                        "Unable to load this conversation."
                    )


            except Exception as e:

                st.error(
                    f"Unable to load chat: {str(e)}"
                )


    st.divider()


    # ==================================================
    # MANAGE CHATS
    # ==================================================

    st.header("⚙️ Manage Chats")


    if st.session_state.chat_sessions:

        session_options = {}

        for chat_session in st.session_state.chat_sessions:

            session_options[
                chat_session["id"]
            ] = chat_session.get(
                "title",
                "New Chat"
            )


        selected_manage_session = st.selectbox(
            "Select conversation",
            options=list(
                session_options.keys()
            ),
            format_func=lambda session_id: (
                session_options[session_id]
            ),
            key="manage_session"
        )


        # ==================================================
        # RENAME CHAT
        # ==================================================

        new_title = st.text_input(
            "New title",
            key="new_chat_title"
        )


        if st.button(
            "✏️ Rename Chat",
            use_container_width=True
        ):

            if not new_title.strip():

                st.error(
                    "Please enter a title."
                )

            else:

                try:

                    response = requests.patch(
                        f"{API_URL}/sessions/"
                        f"{selected_manage_session}",
                        json={
                            "user_id": (
                                st.session_state
                                .user["id"]
                            ),
                            "title": new_title.strip()
                        },
                        timeout=10
                    )

                    response.raise_for_status()

                    data = response.json()


                    if data.get("success"):

                        sessions_response = requests.get(
                            f"{API_URL}/sessions/"
                            f"{st.session_state.user['id']}",
                            timeout=10
                        )

                        sessions_response.raise_for_status()

                        st.session_state.chat_sessions = (
                            sessions_response
                            .json()
                            .get("sessions", [])
                        )

                        st.rerun()


                    else:

                        st.error(
                            data.get(
                                "message",
                                "Unable to rename chat."
                            )
                        )


                except Exception as e:

                    st.error(
                        f"Unable to rename chat: {str(e)}"
                    )


        # ==================================================
        # DELETE CHAT
        # ==================================================

        if st.button(
            "🗑️ Delete Chat",
            use_container_width=True
        ):

            try:

                response = requests.delete(
                    f"{API_URL}/sessions/"
                    f"{selected_manage_session}",
                    params={
                        "user_id": (
                            st.session_state
                            .user["id"]
                        )
                    },
                    timeout=10
                )

                response.raise_for_status()

                data = response.json()


                if data.get("success"):

                    # Reload sessions

                    sessions_response = requests.get(
                        f"{API_URL}/sessions/"
                        f"{st.session_state.user['id']}",
                        timeout=10
                    )

                    sessions_response.raise_for_status()

                    sessions = (
                        sessions_response
                        .json()
                        .get("sessions", [])
                    )

                    st.session_state.chat_sessions = sessions


                    # ------------------------------------------
                    # Open another chat
                    # ------------------------------------------

                    if sessions:

                        st.session_state.active_session_id = (
                            sessions[0]["id"]
                        )


                        history_response = requests.get(
                            f"{API_URL}/sessions/"
                            f"{sessions[0]['id']}/history/"
                            f"{st.session_state.user['id']}",
                            timeout=10
                        )

                        history_response.raise_for_status()

                        st.session_state.messages = (
                            history_response
                            .json()
                            .get("messages", [])
                        )


                    else:

                        # Create replacement chat

                        create_response = requests.post(
                            f"{API_URL}/sessions",
                            json={
                                "user_id": (
                                    st.session_state
                                    .user["id"]
                                )
                            },
                            timeout=10
                        )

                        create_response.raise_for_status()

                        new_session = (
                            create_response
                            .json()
                        )

                        st.session_state.active_session_id = (
                            new_session["session_id"]
                        )

                        st.session_state.messages = []


                    st.rerun()


                else:

                    st.error(
                        data.get(
                            "message",
                            "Unable to delete chat."
                        )
                    )


            except Exception as e:

                st.error(
                    f"Unable to delete chat: {str(e)}"
                )


    else:

        st.info(
            "No conversations available."
        )


    st.divider()


    # ==================================================
    # PDF KNOWLEDGE BASE
    # ==================================================

    st.header("📄 Knowledge Base")


    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )


    if uploaded_files:

        if st.button(
            "Add PDFs to Knowledge Base",
            use_container_width=True
        ):

            with st.spinner(
                "Processing PDFs..."
            ):

                os.makedirs(
                    "data",
                    exist_ok=True
                )

                total_pages = 0

                total_chunks = 0

                successful_files = 0


                for uploaded_file in uploaded_files:

                    file_path = os.path.join(
                        "data",
                        uploaded_file.name
                    )


                    with open(
                        file_path,
                        "wb"
                    ) as f:

                        f.write(
                            uploaded_file.getbuffer()
                        )


                    try:

                        (
                            vectorstore,
                            page_count,
                            chunk_count,
                            document_id
                        ) = add_pdf_to_vectorstore(
                            file_path,
                            uploaded_file.name,
                            st.session_state.user["id"]
                        )


                        total_pages += page_count

                        total_chunks += chunk_count

                        successful_files += 1


                    except Exception as e:

                        st.error(
                            f"Failed to process "
                            f"{uploaded_file.name}: "
                            f"{str(e)}"
                        )


                if successful_files > 0:

                    st.success(
                        "PDF processing completed! ✅"
                    )

                    st.write(
                        f"PDFs processed: "
                        f"{successful_files}"
                    )

                    st.write(
                        f"Total pages: "
                        f"{total_pages}"
                    )

                    st.write(
                        f"Total chunks: "
                        f"{total_chunks}"
                    )


    
    # ==================================================
    # UPLOADED PDFS
    # ==================================================

    st.divider()

    st.subheader("📚 Uploaded PDFs")

    user_id = st.session_state.user["id"]

    # Get only PDFs belonging to the logged-in user
    pdf_files = get_user_pdfs(user_id)

    if pdf_files:

        for pdf in pdf_files:
            st.write(f"📄 {pdf}")

    else:

        st.info("No PDFs uploaded yet.")

    # ==================================================
    # REMOVE PDF
    # ==================================================

    if pdf_files:

        st.subheader("🗑️ Remove PDF")

        pdf_to_remove = st.selectbox(
            "Select a PDF",
            pdf_files
        )

        if st.button(
            "Remove PDF",
            use_container_width=True
        ):

            success, message = delete_pdf(
                pdf_to_remove,
                user_id
            )

            if success:

                st.success(
                    f"{pdf_to_remove} "
                    "removed successfully. ✅"
                )

                st.write(message)

                st.rerun()

            else:

                st.error(message)



# ==================================================
# MAIN CHAT
# ==================================================

if st.session_state.active_session_id is None:

    st.info(
        "Create a new chat to get started."
    )

    st.stop()


# ==================================================
# DISPLAY CHAT HISTORY
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ==================================================
# CHAT INPUT
# ==================================================

user_question = st.chat_input(
    "Ask me anything..."
)


# ==================================================
# PROCESS QUESTION
# ==================================================

if user_question:

    # ==================================================
    # DISPLAY USER MESSAGE
    # ==================================================

    with st.chat_message("user"):

        st.markdown(
            user_question
        )


    # ==================================================
    # SAVE USER MESSAGE LOCALLY
    # ==================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )


    # ==================================================
    # CALL FASTAPI
    # ==================================================

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            try:

                response_data = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "message": user_question,
                        "session_id": str(
                            st.session_state
                            .active_session_id
                        ),
                        "user_id": (
                            st.session_state
                            .user["id"]
                        )
                    },
                    timeout=120
                )


                response_data.raise_for_status()


                # ------------------------------------------
                # Extract AI response
                # ------------------------------------------

                response = (
                    response_data
                    .json()["response"]
                )


                # ------------------------------------------
                # Refresh conversation list
                # ------------------------------------------

                sessions_response = requests.get(
                    f"{API_URL}/sessions/"
                    f"{st.session_state.user['id']}",
                    timeout=10
                )

                sessions_response.raise_for_status()

                st.session_state.chat_sessions = (
                    sessions_response
                    .json()
                    .get("sessions", [])
                )


            except requests.exceptions.ConnectionError:

                response = (
                    "❌ Could not connect to "
                    "the FastAPI backend."
                )


            except requests.exceptions.Timeout:

                response = (
                    "❌ The request took too long "
                    "to complete."
                )


            except Exception as e:

                response = (
                    "❌ Something went wrong:\n\n"
                    f"{str(e)}"
                )


        st.markdown(
            response
        )


    # ==================================================
    # SAVE ASSISTANT MESSAGE LOCALLY
    # ==================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )