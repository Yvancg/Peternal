"""Peternal Web Application.

This module initializes and configures the Flask application for the Peternal platform. 
It sets up necessary configurations for session management and security. Database connections 
are imported from the 'database' module. The application provides users with features related 
to pets tracking, pets memories, and afterlife. Functions for user authentication, registration, 
password validation, and session handling are imported from the 'auth' module.

The app uses SQLite for database operations and Werkzeug for password hashing and verification.
"""
from smtplib import SMTPAuthenticationError

# For debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Loading .env automatically in the dev env
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

# Importing config variables
from config import Config

# Importing from auth.py
from auth import is_valid_email, login_required, register_user, is_password_strong

# Importing from database.py
from database import get_username_email, verify_user, update_password, get_password, get_workouts, user_status, get_user_id_by_email, check_user_exists

# Configure application
app = Flask(__name__)
app.config.from_object(Config)
Session(app)
mail = Mail(app)

# Securely signing emails
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Ensuring server responses are not cached
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Route for the main page
@app.route("/")
@login_required
def index():
    """Show workout program"""
    user_id = int(session["user_id"])
    workouts = None
    workouts = get_workouts(user_id)
    return render_template("index.html", workouts=workouts)

# Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new users"""
    # Render the html
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # Check for username
    if not username:
        flash("Username required.", "danger")
        return render_template("register.html")

    # Check for email
    elif not email:
        flash("Email required.", "danger")
        return render_template("register.html")

    # Check for if email is valid
    elif not is_valid_email(email):
        flash("Invalid email format.", "danger")
        return render_template("register.html")
    
    # Check for password
    elif not password:
        flash("Password required.", "danger")
        return render_template("register.html")
    
    # Check password strength
    elif not is_password_strong(password)[0]:
        flash(f"Password must {is_password_strong(password)[1]}", "danger")
        return render_template("register.html")

    # Check for confirmation
    elif not confirmation:
        flash("Password confirmation required.", "danger")
        return render_template("register.html")

    # Check password matches confirmation
    elif password != confirmation:
        flash("Confirmation doesn't match password.", "danger")
        return render_template("register.html")

    # Check if username or email already exists
    existing_user = check_user_exists(username, email)

    if existing_user["email_exists"]:
        # Email already exists
        flash("Email already registered. Please login.", "info")
        return render_template("login.html")
    elif existing_user["username_exists"]:
        # Username already exists
        flash("Username already taken.", "danger")
        return render_template("register.html")
    else:
        # Username and email are unique, proceed with registration
        if register_user(username, email, password):
            flash("Registration in progress. Check your email.", "info")
            return send_confirmation_email(email)

        else:
            flash("Unexpected error occurred. Please try again.", "danger")

    # Return with show_resend_link as False if any validation fails
    return render_template("register.html", show_resend_link=False)

def send_confirmation_email(email):
    """Send a confirmation email to the user."""
    # Generate token for email confirmation
    token = s.dumps(email, salt='MAIL_CONFIRM_SALT')
    # Create a confirmation link to send by email
    confirm_url = url_for('confirm_email', token=token, _external=True)
    # Create the email message
    html = render_template("email/activate.html", confirm_url=confirm_url)
    subject = "Peternal - Please confirm your email"
    msg = Message(subject, recipients=[email], html=html)

    try:
        # Send the email
        mail.send(msg)
        flash("Please check your email to confirm your registration.", "info")
    except SMTPAuthenticationError:
        # Log the error and notify the user
        app.logger.error("SMTP Authentication failed")
        flash("Email sending failed due to SMTP Authentication error.", "danger")
    except Exception as e:
        app.logger.error("Email sending failed: %s", e)
        flash(f"Email sending failed: {e}", "danger")

    # Return with show_resend_link as True since user is registered but needs to verify email
    return render_template("register.html", show_resend_link=True, email=email)

# Route for email confirmation
@app.route("/confirm_email/<token>")
def confirm_email(token, expiration=3600):
    """Sending email validation"""
    try:
        email = s.loads(token, salt='MAIL_CONFIRM_SALT', max_age=expiration)
    except SignatureExpired:
        flash("The confirmation link has expired", "danger")
        return redirect(url_for('register'))

    # Update the user's status in the database to mark the email as confirmed
    verify_user(email)

    user_id = user_status(email)
    if user_id:
        session["user_id"] = user_id
        flash("Your email has been confirmed!", "success")
        return redirect(url_for('index'))

    else:
        flash("Email verification failed. Please try registering again.", "danger")
        return redirect(url_for('register'))

# Route for resending the verification
@app.route("/resend_verification_email", methods=["POST"])
def resend_verification_email():
    """Route to resend verification email."""
    email = request.form.get("email")
    if email and is_valid_email(email):
        # Resend email logic
        try:
            token = s.dumps(email, salt='MAIL_CONFIRM_SALT')
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template("email/activate.html", confirm_url=confirm_url)
            subject = "Peternal - Please confirm your email"
            msg = Message(subject, recipients=[email], html=html)
            mail.send(msg)
            flash("Verification email resent. Please check your inbox.", "info")
        except SMTPAuthenticationError:
            flash("Email sending failed due to SMTP Authentication error.", "danger")
        except Exception as e:
            flash(f"Email sending failed: {e}", "danger")
    else:
        flash("Invalid email address.", "danger")

    return redirect(url_for('register'))

# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    # Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        username_email = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember") == 'on'

        if not username_email:
            flash("Username or email is required.", "danger")
            return render_template("login.html")

        elif not password:
            flash("Password is required.", "danger")
            return render_template("login.html")

        # Query database for username
        rows = get_username_email(username_email)

        # Ensure username exists
        if rows is None:
            flash("Invalid username/email.", "danger")
            return render_template("login.html", username=username_email)

        # Ensure password is correct
        if not check_password_hash(rows["hash"], password):
            flash("Invalid password.", "danger")
            show_reset_password = True
            return render_template("login.html",
                                   username=username_email,
                                   show_reset_password=show_reset_password)

        # Check if user is verified
        if rows["email_verified"] == 1:
            # Remember which user has logged in
            session["user_id"] = rows["user_id"]

            # Set session permanence based on the 'remember me' checkbox
            session.permanent = remember

            # Redirect user to home page
            flash("Login successful.", "success")
            return render_template("index.html")
        else:
            flash("Please verify your email first.", "danger")
            return render_template("login.html")

    return render_template("login.html", username="", show_reset_password=False)

@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    """Change password"""
    if request.method == "GET":
        return render_template("change.html")

    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirmation = request.form.get("confirmation")

    # Initial form validation
    if not (old_password and new_password and confirmation):
        flash("All fields are required.", "danger")
        return render_template("change.html")

    if new_password == old_password:
        flash("New password must be different from the old password.", "danger")
        return render_template("change.html")

    if new_password != confirmation:
        flash("New passwords do not match.", "danger")
        return render_template("change.html")
    
    # Check password strength
    new_password = request.form.get("new_password")
    is_strong, message = is_password_strong(new_password)
    if not is_strong:
        flash(f"New password must {message}", "danger")
        return render_template("change.html")

    user_id = int(session["user_id"])

    # Database connection for password validation
    row = get_password(user_id)
    if not row or not check_password_hash(row["hash"], old_password):
        flash("Invalid current password.", "danger")
        return render_template("change.html")

    # If old password is valid, then update to new password
    new_hash = generate_password_hash(new_password)
    update_password(user_id, new_hash)
    flash("Password succesfully changed.", "success")
    return redirect(url_for('index'))

# Route for requesting the password reset
@app.route("/request_password_reset", methods=["GET", "POST"])
def request_password_reset():
    """ Directing the user to a page to enter his email to reset the password """
    if request.method == "GET":
        return render_template("request_password_reset.html")

    email = request.form.get("email")
    if email and is_valid_email(email):
        return send_password_reset_email(email)
    else:
        flash("Please enter a valid email address.", "danger")
        return render_template("request_password_reset.html")

def send_password_reset_email(email):
    """ Sending the email to reset the password """
    token = s.dumps(email, salt='PASSWORD_RESET_SALT')
    reset_url = url_for('reset_password', token=token, _external=True)
    html = render_template("email/password_reset.html", reset_url=reset_url)
    subject = "Peternal - Password Reset"
    msg = Message(subject, recipients=[email], html=html)

    try:
        mail.send(msg)
        flash("Check your email for the password reset link.", "info")
        return render_template("login.html")
    except SMTPAuthenticationError:
        app.logger.error("SMTP Authentication failed")
        flash("Email sending failed due to SMTP Authentication error.", "danger")
        return render_template("login.html")
    except Exception as e:
        app.logger.error("Email sending failed: %s", e)
        flash(f"Email sending failed: {e}", "danger")

    return render_template("login.html")

# Route for actually resetting the password
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """ Resetting the password """
    try:
        email = s.loads(token, salt='PASSWORD_RESET_SALT', max_age=3600)
    except SignatureExpired:
        flash("The password reset link has expired.", "danger")
        return render_template("request_password_reset.html")

    if request.method == "GET":
        return render_template("reset_password.html")

    new_password = request.form.get("new_password")
    confirmation = request.form.get("confirmation")

    if new_password != confirmation:
        flash("Passwords do not match.", "danger")
        return render_template("reset_password.html")
    elif not is_password_strong(new_password):
        flash("Password does not meet the required criteria.", "danger")
        return render_template("reset_password.html")

    update_password(email, new_password)
    # After successfully updating the password
    user_id = get_user_id_by_email(email)
    if user_id is None:
        flash("User not found.", "danger")
        return render_template("request_password_reset.html")

    new_hash = generate_password_hash(new_password)
    update_password(user_id, new_hash)

    # Set up user session after password reset
    session["user_id"] = user_id
    flash("Your password has been reset. You are now logged in.", "success")
    return render_template("index.html")

# Route for user logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
