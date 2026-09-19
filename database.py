import os

import mysql.connector

from dotenv import load_dotenv


load_dotenv()


# --------------------------------------------------
# Create Database Connection
# --------------------------------------------------

def get_connection():

    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    return connection


# --------------------------------------------------
# Save Chat Message
# --------------------------------------------------

def save_message(
    session_id: str,
    role: str,
    message: str
):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        INSERT INTO chat_messages
        (session_id, role, message)
        VALUES (%s, %s, %s)
        """

        values = (
            session_id,
            role,
            message
        )

        cursor.execute(
            query,
            values
        )

        connection.commit()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# Get Chat History
# --------------------------------------------------

def get_chat_history(
    session_id: str
):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT role, message
        FROM chat_messages
        WHERE session_id = %s
        ORDER BY id ASC
        """

        cursor.execute(
            query,
            (session_id,)
        )

        results = cursor.fetchall()

        history = []

        for row in results:

            history.append(
                {
                    "role": row["role"],
                    "content": row["message"]
                }
            )

        return history

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

# --------------------------------------------------
# Create User
# --------------------------------------------------

def create_user(
    username: str,
    email: str,
    password_hash: str
):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        INSERT INTO users
        (username, email, password_hash)
        VALUES (%s, %s, %s)
        """

        values = (
            username,
            email,
            password_hash
        )

        cursor.execute(
            query,
            values
        )

        connection.commit()

        return True

    except Exception as e:

        print(f"Failed to create user: {e}")

        return False

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# Get User By Email
# --------------------------------------------------

def get_user_by_email(email: str):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT *
        FROM users
        WHERE email = %s
        """

        cursor.execute(
            query,
            (email,)
        )

        user = cursor.fetchone()

        return user

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()



# --------------------------------------------------
# Create Chat Session
# --------------------------------------------------

def create_chat_session(
    user_id: int,
    title: str = "New Chat"
):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        INSERT INTO chat_sessions
        (user_id, title)
        VALUES (%s, %s)
        """

        cursor.execute(
            query,
            (
                user_id,
                title
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# Get User Chat Sessions
# --------------------------------------------------

def get_chat_sessions(user_id: int):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT id, title, created_at, updated_at
        FROM chat_sessions
        WHERE user_id = %s
        ORDER BY updated_at DESC
        """

        cursor.execute(
            query,
            (user_id,)
        )

        return cursor.fetchall()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# Get Chat Session
# --------------------------------------------------

def get_chat_session(
    session_id: int,
    user_id: int
):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT id, user_id, title
        FROM chat_sessions
        WHERE id = %s
        AND user_id = %s
        """

        cursor.execute(
            query,
            (
                session_id,
                user_id
            )
        )

        return cursor.fetchone()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

# --------------------------------------------------
# Update Chat Session Title
# --------------------------------------------------

def update_chat_session_title(
    session_id: int,
    user_id: int,
    title: str
):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        UPDATE chat_sessions
        SET title = %s
        WHERE id = %s
        AND user_id = %s
        """

        cursor.execute(
            query,
            (
                title,
                session_id,
                user_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# Delete Chat Session
# --------------------------------------------------

def delete_chat_session(
    session_id: int,
    user_id: int
):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        # First verify that the session belongs
        # to the requested user.
        verify_query = """
        SELECT id
        FROM chat_sessions
        WHERE id = %s
        AND user_id = %s
        """

        cursor.execute(
            verify_query,
            (
                session_id,
                user_id
            )
        )

        session = cursor.fetchone()

        if not session:

            return False


        # Delete chat messages
        delete_messages_query = """
        DELETE FROM chat_messages
        WHERE session_id = %s
        """

        cursor.execute(
            delete_messages_query,
            (str(session_id),)
        )


        # Delete session
        delete_session_query = """
        DELETE FROM chat_sessions
        WHERE id = %s
        AND user_id = %s
        """

        cursor.execute(
            delete_session_query,
            (
                session_id,
                user_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()