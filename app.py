import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session

# Importing from auth.py
from auth import User, authenticate_user, register_user, is_password_strong

app = Flask(__name__)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "register"

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Flask-Limiter configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["5 per minute"],
    storage_uri="redis://localhost:6379"
)

# Flask-Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = ')u:L0V91kOOo<sdT6u0?,|o~DtH?2,(/iPRs5!>T6nDG]$a7>h|8:/S%s$<<k'
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom error handler for rate limiting
@app.errorhandler(429)
def rate_limit_handler(e):
    return "Rate limit exceeded", 429

# Route for the main page
@app.route("/")
@login_required
def index():
    """Show workout program"""
    if not current_user.is_authenticated:
        return redirect(url_for('register'))

    user_id = session["user_id"]

    fitness_db = db.execute(
        "SELECT symbol, SUM(shares) AS shares, price FROM transactions WHERE user_id = ? GROUP BY symbol",
        user_id,
    )

    return render_template(
        "index.html",
        database=fitness_db,
        cash=formatted_cash,
        total=formatted_grand_total,
    )

# Route for user login
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and Password are required.")
            return redirect(url_for('login'))

        user = authenticate_user(username, password)
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))

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
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("Username, Password, and Confirmation are required.")
            return redirect(url_for('register'))

        if password != confirmation:
            flash("Passwords must match.")
            return redirect(url_for('register'))

        is_strong, message = is_password_strong(password)
        if not is_strong:
            flash(message)
            return redirect(url_for('register'))

        if register_user(username, password):
            flash("Registration successful. Please log in.")
            return redirect(url_for('login'))
        else:
            flash("Username already exists.")
            return redirect(url_for('register'))

    else:
        return render_template("register.html")

# Other routes and logic as needed...

if __name__ == '__main__':
    app.run(debug=True)
