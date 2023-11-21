from functools import wraps
import re

import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

from flask import redirect, render_template, session

import csv

# Assuming you are using sqlite3 for your database
DATABASE = 'fitness.db'

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def is_password_strong(password):
    """Check the strength of the password."""
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
    pass

def authenticate_user(username, password):
    """Authenticate a user by their username and password."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['hash'], password):
        return user
    return None

def register_user(username, password):
    """Register a new user with a username and password."""
    try:
        conn = get_db_connection()
        hash_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, hash) VALUES (?, ?)', (username, hash_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Additional helper functions as needed...
