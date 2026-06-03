from flask import Blueprint, redirect
from flask_login import login_required, current_user, logout_user
from myapp.app import db

delete_account_bp = Blueprint("delete_account", __name__)

@delete_account_bp.route("/profile/delete", methods=["POST"])
@login_required
def delete_account():
    user = current_user

    db.session.delete(user)
    db.session.commit()

    logout_user()

    return redirect("/")
