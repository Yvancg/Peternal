import os

import sqlite3 as SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import login_required, LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from backup.oldhelpers import is_password_strong

# Configure application
app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

# Configure the maximum number of login attempts
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["5 per minute"]
)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure the use SQLite database
db = SQL.connect("fitness.db")

# Custom error handler
@app.errorhandler(429)
def ratelimite_handler(e):
    """Limits the number of failed logins"""
    return "Number of login attempts exceeded.", 429

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show workout program"""
    user_id = session["user_id"]

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide Username.")
            return redirect(url_for('login'))

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide Password.")
            return redirect(url_for('login'))
        
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password.")
            return redirect(url_for('login'))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new users"""
    # Render the html
    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Stores hash password instead of password
        hash = generate_password_hash(password)
        
        error_field = None

        # Check for username
        if not username:
            flash("Username required.")
            error_field = "username"
            return render_template("register.html")

        # Check for password
        if not password:
            flash("Invalid password.")
            error_field = "password"
            return render_template("register.html", error_field=error_field, username=username)

        # Check for confirmation password
        if not confirmation:
            flash("Confirmation required.")
            error_field = "confirmation"
            return render_template("register.html", error_field=error_field, username=username)

        # Check for matching passwords
        if password != confirmation:
            flash("Passwords do not match.")
            error_field = "password, confirmation"
            return render_template("register.html", error_field=error_field, username=username)

        # Check if the password is strong
        password_strong, message = is_password_strong(password)
        if not password_strong:
            flash(message)
            return render_template("register.html", username=username)

        # Create new user and checks if already registered
        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash)
            )
            db.commit()
            flash("Registration successful.")
        except SQL.IntegrityError:
            flash("Username already registered.")
            return render_template("register.html", error_field='username', username=username)
        except Exception as e:
            flash(f"An error occurred: {e}")
            return render_template("register.html", error_field='database_error', username=username)

        return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    # Your logic here, e.g., loading user from database
    return User.get(user_id)
