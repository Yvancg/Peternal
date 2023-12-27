""" Session storage for OAth2.0 integration using Supabase-py 
to enable users to login using their GitHub account.
"""
from gotrue import SyncSupportedStorage
from flask import session

class FlaskSessionStorage(SyncSupportedStorage):
    """Storage class for Flask session."""
    def __init__(self):
        self.storage = session

    def get_item(self, key: str) -> str | None:
        if key in self.storage:
            return self.storage[key]

    def set_item(self, key: str, value: str) -> None:
        self.storage[key] = value

    def remove_item(self, key: str) -> None:
        if key in self.storage:
            self.storage.pop(key, None)
