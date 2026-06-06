from flask import Blueprint

equipment_bp = Blueprint(
    "equipment",
    __name__,
    url_prefix="/equipment"
)

@equipment_bp.get("/")
def equipment_home():
    return "Equipment module is working"
