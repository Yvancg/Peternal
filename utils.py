from werkzeug.utils import secure_filename
import os
import requests
import csv
from flask_mail import Message
from smtplib import SMTPAuthenticationError
from io import StringIO

# Process photo upload
def save_pet_photo(pet_photo):
    """Function to save the pet photo in a specific dir"""
    if pet_photo.filename == '':
        return None

    filename = secure_filename(pet_photo.filename)
    photo_path = os.path.join('static/pet_photos', filename)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(photo_path), exist_ok=True)

    # Save the file
    pet_photo.save(photo_path)

    return photo_path

# Generic email sending function
def send_email(subject, recipients, html, mail):
    """General function to send emails."""
    msg = Message(subject, recipients=recipients, html=html)
    try:
        mail.send(msg)
        return True, None  # Indicates successful email sending
    except SMTPAuthenticationError as e:
        return False, "SMTP Authentication failed"
    except Exception as e:
        return False, f"Email sending failed: {e}"

# Import dog breeds
def get_sorted_breeds():
    """Importing and sorting all dog breeds from Github"""
    breeds_url = "https://raw.githubusercontent.com/paiv/fci-breeds/main/fci-breeds.csv"
    response = requests.get(breeds_url)
    response.raise_for_status()

    file_like_object = StringIO(response.text)
    reader = csv.DictReader(file_like_object)
    return sorted(row['name'].title() for row in reader)
