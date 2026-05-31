from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()

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

    login_manager.login_view = "auth.login"

    from myapp.app import models

    from myapp.app.routes.auth import auth_bp
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
