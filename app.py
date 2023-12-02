"""Fit 4 Life Web Application.

This module initializes and configures the Flask application for the Fit 4 Life platform. 
It sets up necessary configurations for session management, security, and database connections. 
The application provides users with features related to fitness tracking, workout plans, 
and health metrics. Functions for user authentication, registration, password validation, 
and session handling are imported from the 'auth' module.

The app uses SQLite for database operations and Werkzeug for password hashing and verification.
"""
import os

import sqlite3
from datetime import timedelta
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

# Importing from auth.py
from auth import login_required, register_user, is_valid_email, is_password_strong

from config import SECRET_KEY

# Configure application
app = Flask(__name__)

# Flask-Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = SECRET_KEY
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)  # Remember login for 30 days
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
Session(app)

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
    with sqlite3.connect("fitness.db") as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT workout_id, date, type, duration, intensity FROM workouts WHERE user_id = ?",
            (user_id,)
        )
        workouts = cursor.fetchall()
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
        user_id = register_user(username, email, password)
        if user_id:
            # Starts the session without having to log in
            session["user_id"] = user_id
            flash("Successfully registered.", "success")
            return redirect(url_for('index'))
        else:
            # Sends user to login as user already has credentials
            flash("Already registered", "danger")
            return redirect(url_for('login'))

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
        with sqlite3.connect("fitness.db") as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? OR email = ?", 
                (username_email, username_email,)
            )
            rows = cursor.fetchone()

        # Ensure username exists and password is correct
        if rows is None or not check_password_hash(
            rows["hash"], password
            ):
            flash("Invalid username/email or password.", "danger")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows["user_id"]

        # Set session permanence based on the 'remember me' checkbox
        session.permanent = remember

        # Redirect user to home page
        flash("Login succesful.", "success")
        return redirect(url_for('index'))

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
    with sqlite3.connect("fitness.db") as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT hash FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

    if not row or not check_password_hash(row["hash"], old_password):
        flash("Invalid old password.", "danger")
        return render_template("change.html")

    # Update the user's password
    new_hash = generate_password_hash(new_password)
    cursor.execute("UPDATE users SET hash = ? WHERE user_id = ?", (new_hash, user_id,))
    flash("Password successfully changed.", "success")
    return redirect(url_for('index'))

# Route for user logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
