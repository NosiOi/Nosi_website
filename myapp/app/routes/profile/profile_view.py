from flask import Blueprint, render_template
from flask_login import login_required, current_user

profile_view_bp = Blueprint("profile_view", __name__)

@profile_view_bp.route("/profile")
@login_required
def profile():
    return render_template("app/profile/profile.html", user=current_user)
