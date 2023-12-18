""" Utilities to support the app.py. 
The functions are:
    save_pet_photo
    send_email
    get_sorted_breeds
"""
import os
import csv
from smtplib import SMTPAuthenticationError
from io import StringIO
from werkzeug.utils import secure_filename
import requests
from flask_mail import Message

# Process photo upload
def save_pet_photo(pet_photo):
    """Function to save the pet photo in a specific dir."""
    if pet_photo.filename == '':
        return None

    try:
        filename = secure_filename(pet_photo.filename)
        full_photo_path = os.path.join('static/pet_photos', filename)  # Full path for saving

        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_photo_path), exist_ok=True)

        # Save the file
        pet_photo.save(full_photo_path)

        # Remove 'static/' from the path before returning
        photo_path = full_photo_path.replace('static/', '', 1)

        return photo_path
    except IOError as e:
        raise ValueError("Failed to save pet photo") from e

# Generic email sending function
def send_email(subject, recipients, html, mail):
    """General function to send emails."""
    msg = Message(subject, recipients=recipients, html=html)
    try:
        mail.send(msg)
    except SMTPAuthenticationError as e:
        raise ValueError("SMTP Authentication failed") from e
    except Exception as e:
        raise ValueError("Email sending failed: {{e}}") from e
    return True  # Indicates successful email sending

# Import dog breeds
def get_sorted_breeds():
    """Importing and sorting all dog breeds from Github"""
    breeds_url = "https://raw.githubusercontent.com/paiv/fci-breeds/main/fci-breeds.csv"
    try:
        response = requests.get(breeds_url, timeout=10)
        response.raise_for_status()

        file_like_object = StringIO(response.text)
        reader = csv.DictReader(file_like_object)
        return sorted(row['name'].title() for row in reader)
    except requests.RequestException as e:
        # Handle network errors
        raise ValueError("Failed to fetch breeds data from GitHub") from e
