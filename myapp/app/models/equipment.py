from myapp.app import db


class Equipment(db.Model):
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)

    exercises = db.relationship(
        "Exercise", secondary="exercise_equipment", back_populates="equipment"
    )
