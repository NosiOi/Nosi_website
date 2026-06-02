from flask import Blueprint, redirect, url_for, session
from flask_login import login_user
from myapp.app.models.user import User
from myapp.app import db, oauth

google_bp = Blueprint("google_oauth", __name__)

@google_bp.route("/auth/google")
def google_login():
    google = oauth.create_client("google")
    redirect_uri = url_for("google_oauth.google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@google_bp.route("/auth/google/callback")
def google_callback():
    google = oauth.create_client("google")
    token = google.authorize_access_token()

    userinfo_endpoint = google.server_metadata["userinfo_endpoint"]
    user_info = google.get(userinfo_endpoint).json()

    email = user_info["email"]
    name = user_info["name"]

    user = User.query.filter_by(email=email).first()

    if user:
        from flask_login import logout_user
        logout_user()
        login_user(user)
        return redirect("/profile")

    session["oauth_user"] = {
        "email": email,
        "name": name
    }

    return redirect("/complete-profile")

