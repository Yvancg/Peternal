from werkzeug.utils import secure_filename
import os
from flask_mail import Mail, Message
from smtplib import SMTPAuthenticationError

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

"""
        app.logger.error("SMTP Authentication failed")
        flash("Email sending failed due to SMTP Authentication error.", "danger")
    except Exception as e:
        app.logger.error(f"Email sending failed: {e}")
        flash(f"Email sending failed: {e}", "danger")
"""