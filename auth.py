"""auth.py Functions used for registration and authentication"""
import re
from functools import wraps

from werkzeug.security import generate_password_hash
from flask import redirect, session, url_for, flash
from flask_dance.contrib.google import make_google_blueprint, google
from email_validator import validate_email, EmailNotValidError

from database import create_user, check_user_exists, get_user_id_by_email

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

# Built-in function for email validation
def is_valid_email(email):
    """Validate the email format using email-validator library."""
    try:
        # Validate.
        validate_email(email)
        # Email is valid.
        return True
    except EmailNotValidError as e:
        # Email is not valid, return False.
        return False

# Password strength checker function
def is_password_strong(password):
    """Check the strength of the password using zxcvbn."""
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

# Function to handle Google login
def handle_google_login(user_info):
    """Handle Google login."""
    email = user_info['email']
    username = user_info['username']

    user_exists = check_user_exists(username, email)
    if not user_exists['email_exists']:
        # If user does not exist, create a new user
        create_user(username, email, 'password')
        flash("Account created successfully.", "success")
    else:
        flash("Welcome back!", "success")

    # Set user_id in session
    session["user_id"] = get_user_id_by_email(email)

    return redirect(url_for('index'))
