from .auth import auth_bp
from .dashboard import dashboard_bp
from .plan import plan_api

blueprints = [auth_bp, dashboard_bp, plan_api]
