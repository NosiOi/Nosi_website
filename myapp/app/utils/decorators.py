from functools import wraps
from flask import session, redirect
from myapp.app.models.user import User

def premium_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = User.query.get(session["user"])
        if not user.is_premium:
            return redirect("/premium")
        return f(*args, **kwargs)
    return wrapper


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/auth/login")
        return f(*args, **kwargs)

    return wrapper
