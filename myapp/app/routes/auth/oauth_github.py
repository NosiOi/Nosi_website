from flask import Blueprint, redirect, request, session, current_app
import requests
from flask_login import login_user
from myapp.app.models.user import User
from myapp.app import db

github_bp = Blueprint("github", __name__)


@github_bp.route("/auth/github")
def github_login():
    client_id = current_app.config["GITHUB_CLIENT_ID"]

    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={client_id}&scope=user:email"
    )

    return redirect(github_auth_url)


@github_bp.route("/auth/github/callback")
def github_callback():
    code = request.args.get("code")

    client_id = current_app.config["GITHUB_CLIENT_ID"]
    client_secret = current_app.config["GITHUB_CLIENT_SECRET"]

    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
        },
    ).json()

    access_token = token_res.get("access_token")

    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    email_res = requests.get(
        "https://api.github.com/user/emails",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    primary_email = None
    for e in email_res:
        if e.get("primary"):
            primary_email = e.get("email")

    username = user_res.get("login")
    email = primary_email

    user = User.query.filter_by(email=email).first()

    if user:
        login_user(user)
        return redirect("/profile")

    session["oauth_user"] = {
        "username": username,
        "email": email,
        "provider": "github"
    }

    return redirect("/auth/complete_profile")
