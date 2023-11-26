import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Importing from auth.py
from auth import login_required, register_user, authenticate_user, is_valid_email, is_password_strong

# Configure application
app = Flask(__name__)

# Flask-Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = ')u:L0V91kOOo<sdT6u0?,|o~DtH?2,(/iPRs5!>T6nDG]$a7>h|8:/S%s$<<k'
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
    user_id = session["user_id"]

    if not current_user.is_authenticated:
        return redirect(url_for('register'))

    with sqlite3.connect("fitness.db") as db:
        cursor = db.cursor()
        # Display the workout plan
        cursor.execute(
            "SELECT date, type, duration, intensity FROM workouts WHERE user_id = ? GROUP BY type",
            (user_id,)
        )
        user_data = cursor.fetchone() 

    return render_template("index.html", user_data=user_data,)

# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    # Forget any user_id
    session.clear()

    # User reached route via POST 
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Username is required.")
            return redirect(url_for('login'))

        elif not password:
            flash("Password is required.")
            return redirect(url_for('login'))

        # Query database for username
        with sqlite3.connect("fitness.db") as db:
            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ?", 
                (username,)
            )
            rows = cursor.fetchone()

        # Ensure username exists and password is correct
        if rows is None or not check_password_hash(
            rows["hash"], password
            ):
            flash("Invalid username and/or password.")
            return redirect(url_for('login'))

        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # Redirect user to home page
        return redirect(url_for('index'))

    else:
        return render_template("login.html")

# Route for user logout
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

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
