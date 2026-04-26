from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


from myapp.app.models.user import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object("myapp.app.config.Config")

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    from myapp.app.models.user import User
    from myapp.app import models  # noqa

    from myapp.app.routes.auth import auth_bp
    from myapp.app.routes.dashboard import dashboard_bp
    from myapp.app.routes.plan import plan_api
    from myapp.app.routes.profile import profile_bp
    from myapp.app.routes.assessment import assessment_bp
    from myapp.app.routes.training import training_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(plan_api)
    app.register_blueprint(profile_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(training_bp)

    return app
