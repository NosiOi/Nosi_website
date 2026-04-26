from .auth import auth_bp
from .dashboard import dashboard_bp
from .plan import plan_api
from .profile import profile_bp

blueprints = [auth_bp, dashboard_bp, plan_api, profile_bp]
