# auth.py
import sqlite3
import re
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, session
from functools import wraps

# Requires user to be logged in
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# Authentication function
def authenticate_user(username, password):
    with sqlite3.connect("fitness.db") as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        )
        user_row = cursor.fetchone()

    if user_row and check_password_hash(user_row['hash'], password):
        user = User(id=user_row['user_id'], username=user_row['username'])
        return user 
    return None

# Function to register a new user
def register_user(username, email, password):
    hash_password = generate_password_hash(password)
    with sqlite3.connect("fitness.db") as db:
        cursor = db.cursor()
        # Check if email exists
        cursor.execute(
            "SELECT user_id FROM users WHERE email = ?", (email,)
        )
        if cursor.fetchone():
            return False, "Email already in use."

        try:
            cursor.execute(
                "INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", 
                (username, email, hash_password)
            )
        except sqlite3.IntegrityError:
            return False, "Username already exists."

    return True, "Registration successful."

# Function to check if the email is valid
def is_valid_email(email):
    """Validate the email format."""
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

# Password strength checker function
def is_password_strong(password):
    if len(password) < 8:
        return False, "be at least 8 characters long, "
    if not re.search("[0-9]", password):
        return False, "contain a digit, "
    if not re.search("[A-Z]", password):
        return False, "contain an uppercase letter, "
    if not re.search("[a-z]", password):
        return False, "contain a lowercase letter, "
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "contain a special character."
    return True, "Password is strong."
