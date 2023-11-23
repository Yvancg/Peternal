# auth.py
import sqlite3
import re
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        # Database retrieval logic for user
        db = sqlite3.connect("fitness.db")
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        if user_row:
            return User(id=user_row['id'], username=user_row['username'])
        return None

# Function to authenticate a user
def authenticate_user(username, password):
    db = sqlite3.connect("fitness.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_row = cursor.fetchone()
    if user_row and check_password_hash(user_row['hash'], password):
        return User(id=user_row['id'], username=user_row['username'])
    return None

# Function to register a new user
def register_user(username, password):
    hash_password = generate_password_hash(password)
    db = sqlite3.connect("fitness.db")
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash_password))
        db.commit()
        db.close()
        return True
    except sqlite3.IntegrityError:
        db.close()
        return False

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
