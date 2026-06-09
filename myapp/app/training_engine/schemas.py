from marshmallow import Schema, fields


class MuscleSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    slug = fields.Str()
    description = fields.Str()


class EquipmentSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    tags = fields.Str()
    description = fields.Str()


class ExerciseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    slug = fields.Str()
    description = fields.Str()
    difficulty = fields.Int()
    location = fields.Str()
    movement_pattern = fields.Str()
    risk_level = fields.Int()
    muscles = fields.List(fields.Str())
    equipment = fields.List(fields.Str())
    progression = fields.Str()
    regression = fields.Str()


class TrainingPlanSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    name = fields.Str()
    meta = fields.Str()
    is_active = fields.Bool()


class SessionSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    plan_id = fields.Int()
    title = fields.Str()
    started_at = fields.DateTime()
    finished_at = fields.DateTime()
    data = fields.Str()
