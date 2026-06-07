from flask import Blueprint, request, render_template, redirect, session, flash
from myapp.app.models.verification_code import VerificationCode
from myapp.app.models.user import User
from myapp.app import db, mail
from flask_mail import Message
import random

email_verification_bp = Blueprint("email_verification", __name__, url_prefix="/verify")


def send_verification_email(email, code):
    msg = Message(
        subject="Код підтвердження для NosiFit",
        recipients=[email],
        body=(
            f"Привіт!\n\n"
            f"Ваш код підтвердження для створення акаунту в NosiFit:\n\n"
            f"👉 {code}\n\n"
            f"Код дійсний протягом 10 хвилин.\n"
            f"Якщо ви не надсилали запит — просто ігноруйте цей лист.\n\n"
            f"З повагою,\nКоманда NosiFit"
        )
    )

    msg.html = f"""
    <h2>Ваш код підтвердження</h2>
    <p>Код для входу в <b>NosiFit</b>:</p>
    <h1 style="font-size: 32px; letter-spacing: 4px;">{code}</h1>
    <p>Дійсний 10 хвилин.</p>
    """

    mail.send(msg)


@email_verification_bp.route("/send_code", methods=["POST"])
def send_code():
    email = request.form.get("email")

    if User.query.filter_by(email=email).first():
        flash("Ця пошта вже зареєстрована. Увійдіть у свій акаунт.", "error")
        return redirect("/auth/login")

    session["reg_data"] = request.form.to_dict()

    code = f"{random.randint(100000, 999999)}"

    VerificationCode.query.filter_by(email=email).delete()

    db.session.add(VerificationCode(email=email, code=code))
    db.session.commit()

    send_verification_email(email, code)

    session["pending_email"] = email

    return redirect("/verify/verify_email")



@email_verification_bp.route("/verify_email", methods=["GET", "POST"])
def verify_email():
    if request.method == "GET":
        return render_template("auth/verify_email.html")

    code_input = request.form.get("code")
    email = session.get("pending_email")

    if not email:
        flash("Сесія втрачена. Спробуйте ще раз.", "error")
        return redirect("/auth/register")

    record = VerificationCode.query.filter_by(email=email).first()

    if not record:
        flash("Код не знайдено. Спробуйте ще раз.", "error")
        return redirect("/auth/register")

    if record.code != code_input:
        flash("Невірний код.", "error")
        return redirect("/verify/verify_email")

    session["verified_email"] = email

    db.session.delete(record)
    db.session.commit()

    return redirect("/auth/register_complete")
