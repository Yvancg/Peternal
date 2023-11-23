# auth.py
import sqlite3
import re
from werkzeug.security import check_password_hash, generate_password_hash

# User class for Flask-Login
class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)  # Flask-Login expects the user ID to be a string

    @staticmethod
    def get(user_id):
        db = sqlite3.connect("fitness.db")
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        db.close()
        if user_row:
            return User(id=user_row['id'], username=user_row['username'])
        return None

# Authentication function
def authenticate_user(username, password):
    db = sqlite3.connect("fitness.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_row = cursor.fetchone()
    db.close()

    if user_row and check_password_hash(user_row['hash'], password):
        return User(id=user_row['id'], username=user_row['username'])
    return None

# Function to register a new user
def register_user(username, email, password):
    hash_password = generate_password_hash(password)
    db = sqlite3.connect("fitness.db")
    cursor = db.cursor()

    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        db.close()
        return False, "Email already in use."

    try:
        cursor.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", (username, email, hash_password))
        db.commit()

    except sqlite3.IntegrityError:
        db.close()
        return False, "Username already exists."
    db.close()

    return True, "Registration successful."

# Functino to check if the email is valid
def is_valid_email(email):
    """Validate the email format."""
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

# Password strength checker function
def is_password_strong(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search("[0-9]", password):
        return False, "Password must contain a digit."
    if not re.search("[A-Z]", password):
        return False, "Password must contain an uppercase letter."
    if not re.search("[a-z]", password):
        return False, "Password must contain a lowercase letter."
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain a special character."
    return True, "Password is strong."
