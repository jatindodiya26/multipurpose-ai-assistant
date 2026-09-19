from auth import (
    register_user,
    login_user
)


# --------------------------------------------------
# Register Test User
# --------------------------------------------------

success, message = register_user(
    "Jatin",
    "jatin@example.com",
    "test123"
)

print(message)


# --------------------------------------------------
# Login Test User
# --------------------------------------------------

success, user, message = login_user(
    "jatin@example.com",
    "test123"
)

print(message)

if success:

    print("User ID:", user["id"])
    print("Username:", user["username"])
    print("Email:", user["email"])