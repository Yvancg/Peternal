""" Data Access Layer """
import sqlite3

DATABASE = "fitness.db"

def get_username_email(username_email):
    """ Use for login with either username or email """
    with sqlite3.connect(DATABASE) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
             (username_email, username_email)
        )
        return cursor.fetchone()

def create_user(username, email, password_hash):
    """ Create new user """
    try:
        with sqlite3.connect(DATABASE) as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", 
                (username, email, password_hash)
            )
            db.commit()
            return True
    except sqlite3.IntegrityError:
        flash("Username already taken.")
        return False

def verify_user(email):
    """ Email verification for new registration """
    with sqlite3.connect(DATABASE) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE users SET email_verified = 1 WHERE email = ?", (email,))
        db.commit()

def get_password(user_id):
    """ Go fectch the password to initiate change """
    with sqlite3.connect(DATABASE) as db:
        cursor = db.cursor()
        cursor.execute("SELECT hash FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

def update_password(user_id, new_hash):
    """ Save changed password """
    with sqlite3.connect(DATABASE) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE users SET hash = ? WHERE user_id = ?", (new_hash, user_id,))
        db.commit()

def get_workouts(user_id):
    """ Go fectch workouts """
    with sqlite3.connect(DATABASE) as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT workout_id, date, type, duration, intensity FROM workouts WHERE user_id = ?", 
            (user_id,)
        )
        return cursor.fetchall()
