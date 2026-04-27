from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from myapp.app import db
from myapp.app.models.user_equipment import UserEquipment
from myapp.app.models.equipment import Equipment

equipment_bp = Blueprint("equipment", __name__, url_prefix="/api/equipment")


@equipment_bp.route("/user", methods=["POST"])
@login_required
def update_user_equipment():
    data = request.json
    selected_ids = data.get("equipment_ids", [])

    UserEquipment.query.filter_by(user_id=current_user.id).delete()

    for eq_id in selected_ids:
        db.session.add(UserEquipment(user_id=current_user.id, equipment_id=eq_id))

    db.session.commit()

    return jsonify({"status": "success"})
