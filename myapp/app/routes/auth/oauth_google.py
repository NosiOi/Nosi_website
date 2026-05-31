from flask import Blueprint, redirect, url_for, session, current_app
from authlib.integrations.flask_client import OAuth
from flask_login import login_user
from myapp.app.models.user import User
from myapp.app import db, oauth

google_bp = Blueprint("google_oauth", __name__)

@google_bp.route("/auth/google")
def google_login():
    google = oauth.register(
        name="google",
        client_id=current_app.config["GOOGLE_CLIENT_ID"],
        client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
        access_token_url="https://oauth2.googleapis.com/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        client_kwargs={"scope": "openid email profile"},
    )
    redirect_uri = url_for("google_oauth.google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@google_bp.route("/auth/google/callback")
def google_callback():
    google = oauth.create_client("google")
    token = google.authorize_access_token()
    user_info = google.get("userinfo").json()

    email = user_info["email"]
    name = user_info["name"]

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=name, email=email, password="oauth")
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect("/profile")
