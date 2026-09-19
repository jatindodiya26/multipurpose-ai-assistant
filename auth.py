import bcrypt

from database import (
    create_user,
    get_user_by_email
)


# --------------------------------------------------
# Hash Password
# --------------------------------------------------

def hash_password(password: str) -> str:

    password_bytes = password.encode("utf-8")

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed_password.decode("utf-8")


# --------------------------------------------------
# Verify Password
# --------------------------------------------------

def verify_password(
    password: str,
    password_hash: str
) -> bool:

    password_bytes = password.encode("utf-8")

    hash_bytes = password_hash.encode("utf-8")

    return bcrypt.checkpw(
        password_bytes,
        hash_bytes
    )


# --------------------------------------------------
# Register User
# --------------------------------------------------

def register_user(
    username: str,
    email: str,
    password: str
):

    existing_user = get_user_by_email(
        email
    )

    if existing_user:

        return (
            False,
            "An account with this email already exists."
        )

    password_hash = hash_password(
        password
    )

    success = create_user(
        username,
        email,
        password_hash
    )

    if not success:

        return (
            False,
            "Unable to create the account."
        )

    return (
        True,
        "Account created successfully."
    )


# --------------------------------------------------
# Login User
# --------------------------------------------------

def login_user(
    email: str,
    password: str
):

    user = get_user_by_email(
        email
    )

    if not user:

        return (
            False,
            None,
            "Invalid email or password."
        )

    password_valid = verify_password(
        password,
        user["password_hash"]
    )

    if not password_valid:

        return (
            False,
            None,
            "Invalid email or password."
        )

    return (
        True,
        user,
        "Login successful."
    )