from myapp.app import db
from myapp.app.models.user_equipment import UserEquipment
from myapp.app.models.equipment import Equipment


class EquipmentService:

    @staticmethod
    def get_user_equipment(user):
        items = UserEquipment.query.filter_by(user_id=user.id).all()
        return [{"id": ue.equipment_id} for ue in items]

    @staticmethod
    def add_equipment(user, equipment_id):
        exists = UserEquipment.query.filter_by(
            user_id=user.id,
            equipment_id=equipment_id
        ).first()

        if not exists:
            db.session.add(UserEquipment(user_id=user.id, equipment_id=equipment_id))
            db.session.commit()

    @staticmethod
    def remove_equipment(user, equipment_id):
        UserEquipment.query.filter_by(
            user_id=user.id,
            equipment_id=equipment_id
        ).delete()

        db.session.commit()
