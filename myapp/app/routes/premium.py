from flask import Blueprint, render_template, session, redirect
from myapp.app.models.user import User
from myapp.app import db
from flask_login import login_required

premium_bp = Blueprint("premium", __name__)

@premium_bp.route("/premium")
@login_required
def premium_page():
    user = User.query.get(session["user"])
    return render_template("app/premium.html", user=user)

@premium_bp.route("/premium/activate")
@login_required
def activate_premium():
    user = User.query.get(session["user"])
    user.is_premium = True
    db.session.commit()
    return redirect("/premium")