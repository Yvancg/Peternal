"""Fit 4 Life Web Application.

This module initializes and configures the Flask application for the Fit 4 Life platform. 
It sets up necessary configurations for session management and security,. Database connections 
are imported from the .database' module. The application provides users with features related 
to fitness tracking, workout plans, and health metrics. Functions for user authentication, 
registration, password validation, and session handling are imported from the 'auth' module.

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
from database import get_username_email, verify_user, update_password, get_password, get_workouts, user_status

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

    else:
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check for username
        if not username:
            flash("Username required.", "danger")
            return render_template("register.html")

        # Check for email
        if not email:
            flash("Email required.", "danger")
            return render_template("register.html")

        # Check for password
        if not password:
            flash("Password required.", "danger")
            return render_template("register.html")

        # Check for confirmation
        if not confirmation:
            flash("Confirmation required.", "danger")
            return render_template("register.html")

        # Check for if email is valid
        if not is_valid_email(email):
            flash("Invalid email format.", "danger")
            return render_template("register.html")

        # Check password matches confirmation
        if password != confirmation:
            flash("Passwords must match.", "danger")
            return render_template("register.html")

        # Check password strength
        is_strong, message = is_password_strong(password)
        if not is_strong:
            flash("Password must" + message, "danger")
            return render_template("register.html")

        # Call the function after the checks
        success = register_user(username, email, password)
        app.logger.debug('register user') # Debugging
        if success:
            # Generate token for email confirmation
            token = s.dumps(email, salt='MAIL_CONFIRM_SALT')
            app.logger.debug('token generated') # Debugging

            # Create a confirmation link to send by email
            confirm_url = url_for('confirm_email', token=token, _external=True)

            # Create the email message
            html = render_template("email/activate.html", confirm_url=confirm_url)
            subject = "Fit 4 Life - Please confirm your email"
            msg = Message(subject, recipients=[email], html=html)
            app.logger.debug('Send email') # Debugging
            try:
                # Send the email
                mail.send(msg)
                flash("Please check your email to confirm your registration.", "danger")
                return render_template("register.html")

            except SMTPAuthenticationError:
                # Log the error and notify the user
                app.logger.error("SMTP Authentication failed")
                flash("Email sending failed due to SMTP Authentication error.", "danger")
            except Exception as e:
                app.logger.error("Email sending failed: %s", {e})
                flash(f"Email sending failed: {e}", "danger")

            return render_template("register.html")

        else:
            # Sends user to login as user already has credentials
            flash("Already registered", "danger")
            return redirect(url_for('login'))

    return render_template("register.html")

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

        # Ensure username exists and password is correct
        if rows is None or not check_password_hash(rows["hash"], password):
            flash("Invalid username/email or password.", "danger")
            return render_template("login.html")

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

    return render_template("login.html")

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

    user_id = int(session["user_id"])

    # Database connection for password validation
    row = get_password(user_id)
    app.logger.debug('password row') # Debugging
    print(row) # Debugging
    if not row or not check_password_hash(row[0], old_password):
        flash("Invalid old password.", "danger")
        return render_template("change.html")

    # If old password is valid, then update to new password
    new_hash = generate_password_hash(new_password)
    update_password(user_id, new_hash)
    return redirect(url_for('index'))

# Route for user logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
