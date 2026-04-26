from functools import wraps
from flask import session, redirect


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/auth/login")
        return f(*args, **kwargs)

    return wrapper
