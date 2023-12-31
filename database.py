""" Data Access Layer 
Functions used:
    get_db_connection
    get_username_email
    get_user_id_by_email
    check_user_exists
    create_user
    verify_user
    get_password
    update_password
    user_status
    insert_pet_data
    get_pets
    get_pet_by_id
    update_pet_photo
    update_pet_tracker
"""
import sqlite3
import logging
import contextlib

DATABASE = "petlife.db"

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

def get_username_by_user_id(user_id):
    """ Get the username based on the user ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        username_info = cursor.fetchone()
        return username_info
    
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

def insert_pet_data(user_id, pet_type, pet_name, pet_sex, photo_path, breed, pet_dob, tracker):
    """Save the entries from the pet registration form to the DB"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO pets (user_id, pet_type, pet_name, pet_sex, photo_path, breed, pet_dob, tracker)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, pet_type, pet_name, pet_sex, photo_path, breed, pet_dob, tracker))
            conn.commit()
            return True
    except sqlite3.IntegrityError as e:
        logging.error("Database error occurred: %s", e)
        raise ValueError("Database error occurred") from e

def get_pets(user_id):
    """Retrieve pets for a given user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pets WHERE user_id = ?", (user_id,))
            pets = cursor.fetchall()
            return pets
    except sqlite3.IntegrityError as e:
        logging.error("Database error when fetching pets: %s", e)
        raise ValueError("Database error when fetching pets") from e

def get_pet_by_id(pets_id):
    """Retrieve a pet by its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pets WHERE pets_id = ?", (pets_id,))
        return cursor.fetchone()

def update_pet_photo(pets_id, photo_path):
    """Update the photo path of a pet."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pets SET photo_path = ? WHERE pets_id = ?",
                (photo_path, pets_id,)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError as e:
        logging.error("Database error when updating pet photo: %s", e)
        raise ValueError("Database error when updating pet photo") from e

def update_pet_tracker(pets_id, tracker):
    """Update the tracker info of a pet."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pets SET tracker = ? WHERE pets_id = ?",
                (tracker, pets_id)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError as e:
        logging.error("Database error when updating pet tracker: %s", e)
        raise ValueError("Database error when updating pet tracker") from e

def find_potential_matches(pets_id):
    """ Retrieve potential matches for the given pet."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # First, get the breed and sex of the pet with pets_id
            cursor.execute("SELECT pet_sex, breed FROM pets WHERE pets_id = ?", (pets_id,))
            pet = cursor.fetchone()

            if pet:
                pet_sex, pet_breed = pet["pet_sex"], pet["breed"]

                # Determine the opposite sex
                opposite_sex = "Female" if pet_sex == "Male" else "Male"

                # Then find pets of the same breed but opposite sex
                cursor.execute("""
                    SELECT * FROM pets 
                    WHERE breed = ? AND pet_sex = ? AND pets_id != ?
                """, (pet_breed, opposite_sex, pets_id))

                match = cursor.fetchall()
                return match
            else:
                return []  # No pet found with given pets_id

    except sqlite3.Error as e:
            logging.error("Database error in find_potential_matches: %s", e)
            raise ValueError("Error fetching potential matches from the database") from e

def reject_match(user_id, pet_id, matched_pet_id):
    """Mark a match as rejected."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if the match already exists
            cursor.execute("""
                SELECT * FROM dating WHERE pet_id = ? AND matched_pet_id = ?
            """, (pet_id, matched_pet_id))
            match = cursor.fetchone()

            if match:
                # Update existing match
                cursor.execute("""
                    UPDATE dating SET status = 'rejected' WHERE pet_id = ? AND matched_pet_id = ?
                """, (pet_id, matched_pet_id))
            else:
                # Insert new match
                cursor.execute("""
                    INSERT INTO dating (user_id, pet_id, matched_pet_id, status)
                    VALUES (?, ?, ?, 'rejected')
                """, (user_id, pet_id, matched_pet_id))

            conn.commit()
            return True
    except sqlite3.Error as e:
        logging.error("Database error in reject_match: %s", e)
        raise ValueError("Error updating match status to rejected") from e

def accept_match(user_id, pet_id, matched_pet_id):
    """Mark a match as accepted."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if the match already exists
            cursor.execute("""
                SELECT * FROM dating WHERE pet_id = ? AND matched_pet_id = ?
            """, (pet_id, matched_pet_id))
            match = cursor.fetchone()

            if match:
                # Update existing match
                cursor.execute("""
                    UPDATE dating SET status = 'accepted' WHERE pet_id = ? AND matched_pet_id = ?
                """, (pet_id, matched_pet_id))
            else:
                # Insert new match
                cursor.execute("""
                    INSERT INTO dating (user_id, pet_id, matched_pet_id, status)
                    VALUES (?, ?, ?, 'accepted')
                """, (user_id, pet_id, matched_pet_id))

            conn.commit()
            return True
    except sqlite3.Error as e:
        logging.error("Database error in accept_match: %s", e)
        raise ValueError("Error updating match status to accepted") from e

def update_match_status(pet_id, matched_pet_id, status):
    """ Update the match status of a pet."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Update the status of the match in the dating table
            cursor.execute("""
                UPDATE dating 
                SET status = ? 
                WHERE pet_id = ? OR matched_pet_id = ?
            """, (status, pet_id, matched_pet_id))

            conn.commit()
            return True
    except sqlite3.Error as e:
        logging.error("Database error in update_match_status: %s", e)
        raise ValueError("Error updating match status") from e

def get_accepted_matches(pet_id):
    """Retrieve all accepted matches for a specific pet."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM dating 
                WHERE (pet_id = ? OR matched_pet_id = ?) AND status = 'accepted'
            """, (pet_id, pet_id))
            matches = cursor.fetchall()
            return matches
    except sqlite3.Error as e:
        logging.error("Database error in get_accepted_matches_for_pet: %s", e)
        raise ValueError("Error retrieving matches for pet") from e
