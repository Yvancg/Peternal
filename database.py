""" Data Access Layer """
import sqlite3
import logging

DATABASE = "pets.db"

def get_db_connection():
    """ Centralize the connection logic to the DB """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_username_email(username_email):
    """ Use for login with either username or email """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username_email, username_email,)
        )
        return cursor.fetchone()

def get_user_id_by_email(email):
    """ Associates the user ID with their email"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        return user[0] if user else None

def check_user_exists(username, email):
    """Check if a user with the given username or email already exists."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, email FROM users WHERE username = ? OR email = ?", 
            (username, email)
        )
        result = cursor.fetchone()
        return {
            "username_exists": result and result["username"] == username,
            "email_exists": result and result["email"] == email
        }

def create_user(username, email, password_hash):
    """ Create new user """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", 
                (username, email, password_hash,)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError as e:
        logging.error("Database error occurred: %s", e)
        raise ValueError("Username or email already exists") from e

def verify_user(email):
    """ Email verification for new registration """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email_verified = 1 WHERE email = ?", (email,))
        conn.commit()

def get_password(user_id):
    """ Go fetch the password to initiate change """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

def update_password(user_id, new_hash):
    """ Save changed password """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET hash = ? WHERE user_id = ?", (new_hash, user_id,))
        conn.commit()

def user_status(email):
    """Check the status of the user's email verification and return user_id if verified."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, email_verified FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if user and user["email_verified"] == 1:
            return user["user_id"]
        return None

def insert_pet_data(user_id, pet_type, pet_name, photo_path, breed, pet_dob, tracker):
    """Save the entries from the pet registration form to the DB"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO pets (user_id, pet_type, pet_name, photo_path, breed, pet_dob, tracker)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, pet_type, pet_name, photo_path, breed, pet_dob, tracker))
            conn.commit()
            return True
    except sqlite3.DatabaseError as e:
        logging.error("Database error occurred: %s", e)
        raise ValueError("Database error occurred") from e
