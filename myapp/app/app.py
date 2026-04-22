from flask import Flask
from myapp.app.config import Config
from myapp.app.extensions import db
from flask_migrate import Migrate
from myapp.app.routes.plan_api import plan_api


def create_app():
    app = Flask(__name__)
    app.config.from_object("myapp.app.config.Config")

    db.init_app(app)

    from myapp.app.models import User, Workout, Nutrition, Recovery

    from myapp.app.routes.auth import auth_bp
    from myapp.app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(plan_api)

    return app


app = create_app()

migrate = Migrate(app, db)


if __name__ == "__main__":
    app.run(debug=True)
