from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

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

    login_manager.login_view = "auth.login"

    from myapp.app import models

    from myapp.app.routes.auth import auth_bp
    from myapp.app.routes.dashboard import dashboard_bp
    from myapp.app.routes.plan import plan_bp
    from myapp.app.routes.profile import profile_bp
    from myapp.app.routes.assessment import assessment_bp
    from myapp.app.routes.training import training_bp
    from myapp.app.routes.equipment import equipment_bp
    from myapp.app.routes.questionnaire import questionnaire_bp
    from myapp.app.routes.nutrition import nutrition_bp 

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(questionnaire_bp)
    app.register_blueprint(nutrition_bp)

    return app
