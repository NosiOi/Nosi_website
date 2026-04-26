from flask import Flask
from myapp.app.config import Config
from myapp.app.extensions import db
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.secret_key = "supersecretkey"
    Migrate(app, db)

    from myapp.app import models

    from myapp.app.routes.auth import auth_bp
    from myapp.app.routes.dashboard import dashboard_bp
    from myapp.app.routes.plan import plan_api

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(plan_api)

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
