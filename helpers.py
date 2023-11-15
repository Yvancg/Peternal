from functools import wraps
import re

from flask import redirect, render_template, session

import csv

def is_password_strong(password):
    """Check the strength of the password."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search("[0-9]", password):
        return False, "Password must contain a digit."
    if not re.search("[A-Z]", password):
        return False, "Password must contain an uppercase letter."
    if not re.search("[a-z]", password):
        return False, "Password must contain a lowercase letter."
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain a special character."
    return True, "Password is strong."
