from flask import Blueprint, redirect, url_for, session, current_app
from authlib.integrations.flask_client import OAuth
from flask_login import login_user
from myapp.app.models.user import User
from myapp.app import db, oauth

github_bp = Blueprint("github_oauth", __name__)

@github_bp.route("/auth/github")
def github_login():
    github = oauth.register(
        name="github",
        client_id=current_app.config["GITHUB_CLIENT_ID"],
        client_secret=current_app.config["GITHUB_CLIENT_SECRET"],
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        client_kwargs={"scope": "user:email"},
    )
    redirect_uri = url_for("github_oauth.github_callback", _external=True)
    return github.authorize_redirect(redirect_uri)

@github_bp.route("/auth/github/callback")
def github_callback():
    github = oauth.create_client("github")
    token = github.authorize_access_token()
    user_info = github.get("user").json()
    emails = github.get("user/emails").json()

    email = next((e["email"] for e in emails if e["primary"]), None)
    name = user_info["login"]

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=name, email=email, password="oauth")
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect("/profile")
