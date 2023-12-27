""" Client initiation for OAth2.0 integration using Supabase-py 
to enable users to login using their GitHub account.
"""
import os
from flask import g
from werkzeug.local import LocalProxy
from supabase.client import Client, ClientOptions
from flask_storage import FlaskSessionStorage

url = os.environ.get("SUPABASE_URL", "")
key = os.environ.get("SUPABASE_KEY", "")

def get_supabase() -> Client:
    """ Get Supabase client. """
    if "supabase" not in g:
        g.supabase = Client(
            url,
            key,
            options=ClientOptions(
                storage=FlaskSessionStorage(),
                flow_type="pkce"
            ),
        )
    return g.supabase

supabase: Client = LocalProxy(get_supabase)
