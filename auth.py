"""auth.py Functions used for registration and authentication"""
import re
from functools import wraps

from werkzeug.security import generate_password_hash
from flask import redirect, session, url_for, flash
from flask_oauthlib.client import OAuth
from email_validator import validate_email, EmailNotValidError

from database import create_user, check_user_exists
from config import Config

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

# Google authentication
oauth = OAuth()

def create_google_oauth_client(app):
    """Creates a Google OAuth client."""
    google = oauth.remote_app(
        'google',
        consumer_key=app.config['GOOGLE_CLIENT_ID'],
        consumer_secret=app.config['GOOGLE_CLIENT_SECRET'],
        request_token_params={
            'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
            'prompt': 'select_account'
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )
    return google

def login_with_google():
    """Login with Google."""
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

def authorize():
    """Callback route for Google login."""
    response = oauth.google.authorize_access_token()
    user_info = oauth.google.get('userinfo').json()

    email = user_info['email']
    username = user_info['name']

    user_exists = check_user_exists(username, email)
    if not user_exists['email_exists']:
        # If user does not exist, create a new user
        create_user(username, email, 'password')  # You might want to handle password differently
        flash("Account created successfully.", "success")
    else:
        flash("Welcome back!", "success")

    # Set user_id in session
    session["user_id"] = get_user_id_by_email(email)

    return redirect(url_for('index'))

@google.tokengetter
def get_google_oauth_token():
    """Get the Google OAuth token from the session."""
    return session.get('google_token')