from flask import Flask
from myapp.app.config import Config
from myapp.app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from myapp.app.models import User, Workout, Nutrition, Recovery

        db.create_all()

    from myapp.app.routes.auth import auth_bp
    from myapp.app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
