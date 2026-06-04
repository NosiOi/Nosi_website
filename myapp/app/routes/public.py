from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__, url_prefix="")

@public_bp.route("/about")
def about():
    return render_template("public/about.html")

@public_bp.route("/pricing")
def pricing():
    return render_template("public/pricing.html")

@public_bp.route("/demo")
def demo():
    return render_template("public/demo.html")
