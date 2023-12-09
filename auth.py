"""auth.py Functions used for registration and authentication"""
import re
from functools import wraps
from werkzeug.security import generate_password_hash
from flask import redirect, session

from database import create_user

# Requires user to be logged in
def login_required(f):
    """Decorate routes to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Function to register a new user
def register_user(username, email, password):
    """Registers a new user"""
    # Stores hash password instead of password
    password_hash = generate_password_hash(password)
    # Create new user and checks if already registered
    return create_user(username, email, password_hash)

# Function to check if the email is valid
def is_valid_email(email):
    """Validate the email format."""
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None


# Password strength checker function
def is_password_strong(password):
    """ Ensure the password is strong"""
    if len(password) < 8:
        return False, "be at least 8 characters long, "
    if not re.search("[0-9]", password):
        return False, "contain a digit, "
    if not re.search("[A-Z]", password):
        return False, "contain an uppercase letter, "
    if not re.search("[a-z]", password):
        return False, "contain a lowercase letter, "
    if not re.search(r"[^\w]", password):
        return False, "contain a special character."
    return True, "Password is strong."
