import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

# Importing from auth.py
from auth import login_required, register_user, authenticate_user, is_valid_email, is_password_strong

from config import SECRET_KEY

# Configure application
app = Flask(__name__)

# Flask-Session configuration
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = SECRET_KEY
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

        if not username_email:
            flash("Username or email is required.")
            return redirect(url_for('login'))

        elif not password:
            flash("Password is required.")
            return redirect(url_for('login'))

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
            flash("Invalid username/email or password.")
            return redirect(url_for('login'))

        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # Redirect user to home page
        return redirect(url_for('index'))

    return render_template("login.html")

# Route for user logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

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
            flash("Username required.")
            return redirect(url_for('register'))

        # Check for email
        if not email:
            flash("Email required.")
            return redirect(url_for('register'))

        # Check for password
        if not password:
            flash("Password required.")
            return redirect(url_for('register'))

        # Check for confirmation
        if not confirmation:
            flash("Confirmation required.")
            return redirect(url_for('register'))

        # Check for if email is valid
        if not is_valid_email(email):
            flash("Invalid email format.")
            return redirect(url_for('register'))

        # Check password matches confirmation
        if password != confirmation:
            flash("Passwords must match.")
            return redirect(url_for('register'))

        # Check password strength
        is_strong, message = is_password_strong(password)
        if not is_strong:
            flash("Password must" + message)
            return redirect(url_for('register'))

        # Call the function after the checks
        user_id = register_user(username, email, password)
        if user_id:
            # Starts the session without having to log in
            session["user_id"] = user_id
            return redirect(url_for('index'))
        else:
            # Sends user to login as user already has credentials
            flash("Already registered")
            return redirect(url_for('login'))

"""
        # Stores hash password instead of password
        hash = generate_password_hash(password)

        # Create new user and checks if already registered
        try:
            with sqlite3.connect("fitness.db") as db:
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash)
                )
                user_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            flash("Already registered")
            return redirect(url_for('login'))

        # Starts the session without having to log in
        session["user_id"] = user_id

        return redirect("/")
"""