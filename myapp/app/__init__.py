from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
oauth = OAuth()

from myapp.app.models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object("myapp.app.config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    oauth.init_app(app)

    login_manager.login_view = "auth.login"

    app.config["GOOGLE_CLIENT_ID"] = "твій_id"
    app.config["GOOGLE_CLIENT_SECRET"] = "твій_secret"
    app.config["GITHUB_CLIENT_ID"] = "твій_id"
    app.config["GITHUB_CLIENT_SECRET"] = "твій_secret"

    from myapp.app.routes.auth_main import auth_bp
    from myapp.app.routes.dashboard import dashboard_bp
    from myapp.app.routes.plan import plan_bp
    from myapp.app.routes.assessment import assessment_bp
    from myapp.app.routes.training import training_bp
    from myapp.app.routes.equipment import equipment_bp
    from myapp.app.routes.questionnaire import questionnaire_bp
    from myapp.app.routes.nutrition import nutrition_bp
    from myapp.app.routes.premium import premium_bp

    from myapp.app.routes.profile.profile_view import profile_view_bp
    from myapp.app.routes.profile.profile_update import profile_update_bp
    from myapp.app.routes.profile.password_change import password_change_bp
    from myapp.app.routes.profile.email_change import email_change_bp

    from myapp.app.routes.auth.oauth_google import google_bp
    from myapp.app.routes.auth.oauth_github import github_bp

    app.register_blueprint(google_bp)
    app.register_blueprint(github_bp)

    app.register_blueprint(profile_view_bp)
    app.register_blueprint(profile_update_bp)
    app.register_blueprint(password_change_bp)
    app.register_blueprint(email_change_bp)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(questionnaire_bp)
    app.register_blueprint(nutrition_bp)
    app.register_blueprint(premium_bp)

    return app
