"""Peternal Web Application.

This module initializes and configures the Flask application for the Peternal platform. 
It sets up necessary configurations for session management and security. The application 
provides users with features related to pets tracking, pets memories, and afterlife. 
Database connections are imported from the 'database' module. Functions for user authentication, 
registration, password validation, and session handling are imported from the 'auth' module.
Here are the functions in the order they appear:
    def after_request(response):
    get_username_info():
    def index():
    def register():
    def send_confirmation_email(email):
    def confirm_email(token, expiration=3600):
    def resend_verification_email():
    def login():
    def login_with_github():
    def callback():
    def change():
    def request_password_reset():
    def send_password_reset_email(email):
    def reset_password(token):
    def logout():
    def add_pet():
    def edit_photo():
    def edit_tracker():
    def dating():
    def get_pet_details(pets_id):
    def get_potential_matches(pets_id):
    def reject_match_route(pet_id, matched_pet_id):
    def accept_match_route(pet_id, matched_pet_id):
    def get_accepted_matches_route(pet_id):
The app uses SQLite for database operations and Werkzeug for password hashing and verification.
"""

# For debugging
import logging

# Loading .env automatically in the dev env
from dotenv import load_dotenv

from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_mail import Mail
from flask_session import Session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.contrib.github import make_github_blueprint, github
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

# Importing config variables
from config import Config
from auth import is_valid_email, login_required, register_user, is_password_strong
from database import (get_username_email, verify_user, update_password, get_pet_by_id, create_user,
                      get_password, user_status, insert_pet_data, get_pets, find_potential_matches,
                      get_user_id_by_email, check_user_exists, update_pet_photo, update_pet_tracker,
                      reject_match, accept_match, get_accepted_matches, get_username_by_user_id)
from utils import save_pet_photo, send_email, get_sorted_breeds, sanitize_email, sanitize_username

load_dotenv()

# Configure logging messages
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configure application
app = Flask(__name__)
app.config.from_object(Config)
Session(app)
mail = Mail(app)

# Initialize Google OAuth Blueprint
google_blueprint = make_google_blueprint(
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    scope=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
    redirect_url='http://127.0.0.1:5000/login/google/callback'
)
app.register_blueprint(google_blueprint, url_prefix="/login")

facebook_blueprint = make_facebook_blueprint(
    client_id="FACEBOOK_APP_ID",
    client_secret="FACEBOOK_APP_SECRET",
    scope="email",
    redirect_to="facebook_login"
)

app.register_blueprint(facebook_blueprint, url_prefix="/login/facebook")

# Initialize Github OAuth Blueprint
github_blueprint = make_github_blueprint(
    client_id=app.config['GITHUB_CLIENT_ID'],
    client_secret=app.config['GITHUB_CLIENT_SECRET'],
    scope=['user:email', 'read:user']
)
app.register_blueprint(github_blueprint, url_prefix="/login")

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

# Route for username display for the session
@app.context_processor
def get_username_info():
    """Inject user info into the template"""
    if "user_id" in session:
        user_id = session["user_id"]
        username_info = get_username_by_user_id(user_id)  # Function to get user info from DB
        return {'logged_in_user': username_info}  # 'user_info' should have username
    return {'logged_in_user': None}

# Route for the main page
@app.route("/")
@login_required
def index():
    """Show pets owned"""
    user_id = session["user_id"]
    try:
        pets = get_pets(user_id)
    except ValueError as e:
        flash(str(e), 'danger')
        logging.error("Error fetching pets: %s", e)
        pets = []  # Default to an empty list in case of an error

    return render_template("index.html", pets=pets)

# Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new users"""
    # Render the html
    if request.method == "GET":
        return render_template("login.html")

    username = sanitize_username(request.form.get("username").lower())
    email = sanitize_email(request.form.get("email"))
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # Check for username
    if not username:
        flash("Username required.", "danger")
        return render_template("login.html", error_field="username")

    # Check for email
    if not email:
        flash("Email required.", "danger")
        return render_template("login.html", error_field="email")

    # Check for if email is valid
    if not is_valid_email(email):
        flash("Invalid email format.", "danger")
        return render_template("login.html", error_field="email")

    # Check for password
    if not password:
        flash("Password required.", "danger")
        return render_template("login.html", error_field="password")

    # Check password strength
    if not is_password_strong(password)[0]:
        flash(f"Password must {is_password_strong(password)[1]}", "danger")
        return render_template("login.html", error_field="password")

    # Check for confirmation
    if not confirmation:
        flash("Password confirmation required.", "danger")
        return render_template("login.html", error_field="confirmation")

    # Check password matches confirmation
    if password != confirmation:
        flash("Confirmation doesn't match password.", "danger")
        return render_template("login.html", error_field="confirmation")

    # Check if username or email already exists
    existing_user = check_user_exists(username, email)

    if existing_user["email_exists"]:
        # Email already exists
        flash("Email already registered. Please login.", "info")
        return redirect(url_for('login'))

    if existing_user["username_exists"]:
        # Username already exists
        flash("Username already taken.", "danger")
        return render_template("login.html", error_field="username")

    try:
        # Attempt to register user
        if register_user(username, email, password):
            return send_confirmation_email(email)
        else:
            raise ValueError("Registration failed")

    except ValueError as e:
        flash("Unexpected error occurred. Please try again.", "danger")
        logging.error("Unexpected registration error: %s", e)

    # Return with show_resend_link as False if any validation fails
    return render_template("login.html", show_resend_link=False)

def send_confirmation_email(email):
    """Send a confirmation email to the user."""
    # Generate token for email confirmation
    token = s.dumps(email, salt='MAIL_CONFIRM_SALT')
    # Create a confirmation link to send by email
    confirm_url = url_for('confirm_email', token=token, _external=True)
    # Create the email message
    html = render_template("email/activate.html", confirm_url=confirm_url)
    subject = "Peternal - Please confirm your email"

    try:
        send_email(subject, [email], html, mail)
        flash("Please check your email to confirm your registration.", "info")
    except ValueError as e:
        flash(str(e), 'danger')
        logging.error("Failed to send confirmation email: %s", e)

    # Return with show_resend_link as True since user is registered but needs to verify email
    return render_template("login.html", show_resend_link=True, email=email)

# Route for email confirmation
@app.route("/confirm_email/<token>")
def confirm_email(token, expiration=3600):
    """Sending email validation"""
    try:
        email = s.loads(token, salt='MAIL_CONFIRM_SALT', max_age=expiration)
    except SignatureExpired as e:
        flash("The confirmation link has expired", "danger")
        logging.error("Confirmation link expired: %s", e)
        return redirect(url_for('login'))

    # Update the user's status in the database to mark the email as confirmed
    verify_user(email)

    user_id = user_status(email)
    if user_id:
        session["user_id"] = user_id
        flash("Your email has been confirmed!", "success")
        return redirect(url_for('index'))

    else:
        flash("Email verification failed. Please try registering again.", "danger")
        logging.error("Email verification failure: %s", e)
        return redirect(url_for('login'))

# Route for resending the verification
@app.route("/resend_verification_email", methods=["POST"])
def resend_verification_email():
    """Route to resend verification email."""
    email = sanitize_email(request.form.get("email"))
    if email and is_valid_email(email):
        # Resend email logic
        token = s.dumps(email, salt='MAIL_CONFIRM_SALT')
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template("email/activate.html", confirm_url=confirm_url)
        subject = "Peternal - Please confirm your email"

        try:
            send_email(subject, [email], html, mail)
            flash("Verification email resent. Please check your inbox.", "info")

        except ValueError as e:
            flash(str(e), 'danger')
            logging.error("Failed to resend verification email: %s", e)

    else:
        flash("Email not valid.", "danger")

    return render_template("login.html")

# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    # Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        username_email = request.form.get("username").lower()
        password = request.form.get("password")
        remember = request.form.get("remember") == 'on'

        # Ensure username/email is entered
        if not username_email:
            flash("Username or email is required.", "danger")
            return render_template("login.html", error_field="email")

        # Query database for username
        rows = get_username_email(username_email)

        # Ensure username exists
        if rows is None:
            flash("Invalid username/email.", "danger")
            return render_template("login.html", username=username_email, error_field="email")

        # Ensure password is entered
        if not password:
            flash("Password is required.", "danger")
            return render_template("login.html", error_field="password")

        # Ensure password is correct
        if not check_password_hash(rows["hash"], password):
            flash("Invalid password.", "danger")
            show_reset_password = True
            return render_template("login.html",
                                   username=username_email,
                                   show_reset_password=show_reset_password,
                                   error_field="password")

        # Check if user is verified
        if rows["email_verified"] == 1:
            # Remember which user has logged in
            session["user_id"] = rows["user_id"]

            # Set session permanence based on the 'remember me' checkbox
            session.permanent = remember

            # Redirect user to home page
            flash("Login successful.", "success")
            return redirect(url_for('index'))
        else:
            flash("Please verify your email first.", "danger")
            return render_template("login.html")

    return render_template("login.html", username="", show_reset_password=False)

# Login with Google
@app.route('/login/google')
def login_with_google():
    """ Log in with Google """
    return redirect(url_for("google.login"))

@app.route('/login/google/callback')
def google_callback():
    """ Callback route for Google login """
    if not google_blueprint.session.authorized:
        flash("Failed to authenticate with Google.", "danger")
        return redirect(url_for("index"))

    resp = google_blueprint.session.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_info = resp.json()
        email = user_info["email"]
        username = user_info.get("name", email.split('@')[0])

        user_exists = check_user_exists(username, email)
        if not user_exists['email_exists']:
            create_user(username, email, 'password')
            flash("Account created successfully.", "success")
        else:
            session["user_id"] = get_user_id_by_email(email)
            flash("Welcome back!", "success")
        return redirect(url_for('index'))
    else:
        flash("Failed to fetch user info from Google.", "danger")
        return redirect(url_for('login'))

# Login with Facebook
@app.route("/login/facebook")
def login_with_facebook():
    """ Log in with Facebook """
    if not facebook_blueprint.session.authorized:
        return redirect(url_for("facebook.login"))

    resp = facebook_blueprint.session.get("/me?fields=id,name,email")
    if resp.ok:
        facebook_info = resp.json()
        # Process the Facebook info (e.g., store in database, create session)
        return "Facebook login successful!"  # Redirect as necessary
    else:
        return "Failed to fetch user info from Facebook."


# Login with GitHub
@app.route("/login/github")
def login_with_github():
    """ Log in with GitHub """
    if not github.authorized:
        return redirect(url_for('github.login'))
    return redirect(url_for('github_callback'))

@app.route("/login/github/callback")
def github_callback():
    """ Callback route for GitHub login """
    if not github_blueprint.session.authorized:
        flash("Failed to authenticate with GitHub.", "danger")
        return redirect(url_for('index'))
    
    try:
        resp = github_blueprint.session.get("/user")
        if resp.ok:
            user_info = resp.json()
            username = user_info.get("login")

            email_resp = github_blueprint.session.get("/user/emails")
            if email_resp.ok:
                emails = email_resp.json()
                try:
                    email = next(e['email'] for e in emails if e['primary'])
                except StopIteration:
                    flash("No primary email found.", "danger")
                    return redirect(url_for('index'))

                user_exists = check_user_exists(username, email)
                if user_exists and not user_exists['email_exists']:
                    create_user(username, email, 'password')
                    flash("Account created successfully.", "success")
                elif user_exists:
                    flash("Account already exists.", "danger")
                    return redirect(url_for('login'))
                
                # Remember which user has logged in
                session["user_id"] = user_exists['user_id']
                session.permanent = True

                return redirect(url_for('index'))
            else:
                flash("Failed to fetch email from GitHub.", "danger")
                return redirect(url_for('index'))
        else:
            flash("Failed to authenticate with GitHub.", "danger")
            return redirect(url_for("index"))
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("index"))

# Route for changing the password
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
        return render_template("change.html", error_field="old_password")

    if new_password == old_password:
        flash("New password must be different from the old password.", "danger")
        return render_template("change.html", error_field="new_password")

    if new_password != confirmation:
        flash("New passwords do not match.", "danger")
        return render_template("change.html", error_field="confirmation")

    # Check password strength
    new_password = request.form.get("new_password")
    is_strong, message = is_password_strong(new_password)
    if not is_strong:
        flash(f"New password must {message}", "danger")
        return render_template("change.html", error_field="new_password")

    user_id = int(session["user_id"])

    # Database connection for password validation
    row = get_password(user_id)
    if not row or not check_password_hash(row["hash"], old_password):
        flash("Invalid current password.", "danger")
        return render_template("change.html", error_field="old_password")

    # If old password is valid, then update to new password
    new_hash = generate_password_hash(new_password)
    update_password(user_id, new_hash)
    flash("Password successfully changed.", "success")
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
        return render_template("request_password_reset.html", error_field="email")

def send_password_reset_email(email):
    """ Sending the email to reset the password """
    token = s.dumps(email, salt='PASSWORD_RESET_SALT')
    reset_url = url_for('reset_password', token=token, _external=True)
    html = render_template("email/password_reset.html", reset_url=reset_url)
    subject = "Peternal - Password Reset"

    send_email(subject, [email], html, mail)
    flash("Check your email for the password reset link.", "info")

    return render_template("login.html")

# Route for actually resetting the password
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """ Resetting the password """
    try:
        email = s.loads(token, salt='PASSWORD_RESET_SALT', max_age=3600)
    except SignatureExpired as e:
        flash("The password reset link has expired.", "danger")
        logging.error("Reset link expired: %s", e)
        return render_template("request_password_reset.html")

    if request.method == "GET":
        return render_template("reset_password.html", token=token)

    new_password = request.form.get("new_password")
    confirmation = request.form.get("confirmation")

    # Handling wrong password formats
    if new_password != confirmation:
        flash("Passwords do not match.", "danger")
        return render_template("reset_password.html", error_field="confirmation")

    if not is_password_strong(new_password):
        flash("Password does not meet the required criteria.", "danger")
        return render_template("reset_password.html", error_field="password")

    # After successfully updating the password
    user_id = get_user_id_by_email(email)
    if user_id is None:
        flash("User not found.", "danger")
        return render_template("request_password_reset.html")

    # Updating the password in the database
    new_hash = generate_password_hash(new_password)
    update_password(user_id, new_hash)

    # Set up user session after password reset
    session["user_id"] = user_id
    flash("Your password has been reset. You are now logged in.", "success")
    return redirect(url_for('index'))

# Route for user logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# Route for adding pets
@app.route("/add_pet", methods=["GET", "POST"])
@login_required
def add_pet():
    """Users can add their pets once logged in"""
    if request.method == "GET":
        breeds = get_sorted_breeds()
        return render_template("add_pet.html", breeds=breeds)

    if request.method == "POST":
        pet_type = request.form.get("pet_type")
        pet_name = request.form.get("pet_name")
        pet_sex = request.form.get("pet_sex")
        pet_photo = request.files.get("pet_photo")
        breed = request.form.get("breeds")
        pet_dob = request.form.get("pet_dob")
        tracker = request.form.get("tracker")

        max_size = 5 * 1024 * 1024  # 5MB

        if pet_photo and len(pet_photo.read()) > max_size:
            flash("The file is too large. Please select a file smaller than 5MB.", 'danger')
            return render_template("add_pet.html")

        pet_photo.seek(0)  # Reset the file read pointer

        try:
            # Ensure a photo was uploaded
            photo_path = save_pet_photo(pet_photo)
            user_id = int(session["user_id"])

            if not insert_pet_data(user_id, pet_type, pet_name, pet_sex, photo_path, breed, pet_dob, tracker):
                raise ValueError("Failed to add pet data to the database.")
            flash("Your pet has been added!", "success")
            return redirect(url_for('index'))

        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('add_pet'))

# Route for editing pet profile pic
@app.route('/edit_photo', methods=['POST'])
def edit_photo():
    """ Modal form for editing pet photo """
    pets_id = request.form['petId']
    pet_photo = request.files['petPhoto']

    if pet_photo:
        try:
            photo_path = save_pet_photo(pet_photo)

            if photo_path:
                update_pet_photo(pets_id, photo_path)
                flash("Pet photo updated successfully!", "success")
            else:
                flash("Photo upload failed. Please try again.", "danger")

        except ValueError as e:
            flash(str(e), "danger")

    return redirect("/")

# Route for editing the tracker
@app.route('/edit_tracker', methods=['POST'])
def edit_tracker():
    """ Modal form for editing pet tracker """
    pets_id = request.form['petId']
    tracker = request.form['petTracker']

    try:
        update_pet_tracker(pets_id, tracker)
        flash("Tracker information updated successfully!", "success")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect("/")

# Route for dating
@app.route('/dating')
@login_required
def dating():
    """ Dating page """
    user_id = session["user_id"]

    try:
        pets = get_pets(user_id)
        return render_template('dating.html', user_pets=pets)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('dating'))

# Route for getting pet details for dating
@app.route('/get_pet_details/<int:pets_id>')
def get_pet_details(pets_id):
    """ Getting pet details for dating """
    pet = get_pet_by_id(pets_id)
    pet_dict = dict(pet) if pet else {}
    return jsonify(pet_dict)

@app.route('/get_potential_matches/<int:pets_id>')
def get_potential_matches(pets_id):
    """ Find potential matches based on pets_id """
    try:
        matches = find_potential_matches(pets_id)
        matches_list = [dict(match) for match in matches]  # Convert to list of dicts
        return jsonify(matches_list)
    except ValueError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reject_match/<int:pet_id>/<int:matched_pet_id>', methods=['POST'])
@login_required
def reject_match_route(pet_id, matched_pet_id):
    """ Reject a match """
    user_id = session["user_id"]
    try:
        if reject_match(user_id, pet_id, matched_pet_id):
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "Failed to reject match"}), 500
    except ValueError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/accept_match/<int:pet_id>/<int:matched_pet_id>', methods=['POST'])
@login_required
def accept_match_route(pet_id, matched_pet_id):
    """ Accept a match """
    user_id = session["user_id"]
    try:
        if accept_match(user_id, pet_id, matched_pet_id):
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "Failed to accept match"}), 500
    except ValueError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_accepted_matches/<int:pet_id>')
@login_required
def get_accepted_matches_route(pet_id):
    """ Get accepted matches for a specific pet """
    try:
        matches = get_accepted_matches(pet_id)
        return jsonify(matches)
    except ValueError as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(ssl_context='adhoc')

@app.route("/privacy-policy")
def privacy_policy():
    """ Privacy policy page """
    return render_template("privacy_policy.html")
