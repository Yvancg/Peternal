from functools import wraps
import re

from flask import redirect, render_template, session

import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid



def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

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
