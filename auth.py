"""auth.py Functions used for registration and authentication"""
import re
from functools import wraps

# Loading .env automatically in the dev env
from dotenv import load_dotenv

from werkzeug.security import generate_password_hash
from flask import redirect, session, url_for, flash, Blueprint
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.contrib.github import make_github_blueprint, github
from email_validator import validate_email, EmailNotValidError

from database import create_user, check_user_exists, get_user_id_by_email
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

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

# Initialize Google OAuth Blueprint
google_blueprint = make_google_blueprint(
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    scope=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
    redirect_url='http://127.0.0.1:5000/auth/login/google/callback'
)
auth_bp.register_blueprint(google_blueprint, url_prefix="/login/google")

# Initialize Facebook OAuth Blueprint
facebook_blueprint = make_facebook_blueprint(
    client_id=Config.FACEBOOK_APP_ID,
    client_secret=Config.FACEBOOK_APP_SECRET,
    scope="email",
    redirect_to="facebook_login"
)
auth_bp.register_blueprint(facebook_blueprint, url_prefix="/login/facebook")

# Initialize GitHub OAuth Blueprint
github_blueprint = make_github_blueprint(
    client_id=Config.GITHUB_CLIENT_ID,
    client_secret=Config.GITHUB_CLIENT_SECRET,
    scope=['user:email', 'read:user']
)
auth_bp.register_blueprint(github_blueprint, url_prefix="/github")
