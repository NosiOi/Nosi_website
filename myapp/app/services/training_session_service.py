from myapp.app import db
from myapp.app.models.training_session import TrainingSession, SessionExercise
from myapp.app.services.training_engine_service import TrainingEngineService
from myapp.app.training_engine.models.exercise import Exercise


class TrainingSessionService:
    @staticmethod
    def start_session(user, fatigue_before=None):
        plan = TrainingEngineService.generate_plan(user, week=1)
        day_key = next(iter(plan.days.keys()))
        day = plan.days[day_key]

        session = TrainingSession(
            user_id=user.id, fatigue_before=fatigue_before, status="active"
        )
        db.session.add(session)
        db.session.flush()

        for ex in day["exercises"]:
            se = SessionExercise(
                session_id=session.id,
                exercise_id=ex["exercise"]["id"],
                sets_planned=ex.get("sets") or 0,
                reps_planned=ex.get("reps"),
                load_planned=ex.get("load") or 0,
            )
            db.session.add(se)

        db.session.commit()
        return session

    @staticmethod
    def add_exercise(session, exercise_id):
        existing = SessionExercise.query.filter_by(
            session_id=session.id, exercise_id=exercise_id
        ).first()

        if existing:
            return existing

        se = SessionExercise(
            session_id=session.id, exercise_id=exercise_id, sets_planned=0
        )
        db.session.add(se)
        db.session.commit()
        return se

    @staticmethod
    def update_exercise(session, exercise_id, data):
        se = SessionExercise.query.filter_by(
            session_id=session.id, exercise_id=exercise_id
        ).first()

        if not se:
            se = TrainingSessionService.add_exercise(session, exercise_id)

        se.sets_done = data.get("sets_done", se.sets_done)
        se.reps_done = data.get("reps_done", se.reps_done)
        se.load_done = data.get("load_done", se.load_done)
        se.rpe = data.get("rpe", se.rpe)

        db.session.commit()
        return se

    @staticmethod
    def _compute_session_load(session):
        user = session.user

        total_load = 0.0
        muscle_loads = {}

        age = user.age or 25
        sex = (user.sex or "unspecified").lower()
        weight = user.weight or 70.0
        height = user.height or 175.0
        experience = (user.experience or "beginner").lower()
        activity = (user.activity or "moderate").lower()
        workouts_per_week = user.workouts_per_week or 3

        perf = user.performance_state
        pushups = getattr(perf, "pushups", 0) if perf else 0
        squats = getattr(perf, "squats", 0) if perf else 0
        situps = getattr(perf, "situps", 0) if perf else 0
        strength_index = (
            (pushups + squats + situps) / 3 if (pushups or squats or situps) else 0
        )

        if age < 18:
            age_factor = 0.85
        elif age <= 35:
            age_factor = 1.0
        elif age <= 50:
            age_factor = 0.92
        else:
            age_factor = 0.85

        sex_factor = 1.0 if sex == "male" else 0.87

        bmi = weight / ((height / 100) ** 2)
        if bmi < 18.5:
            bmi_factor = 0.9
        elif bmi <= 25:
            bmi_factor = 1.0
        elif bmi <= 30:
            bmi_factor = 1.05
        else:
            bmi_factor = 1.1

        if experience == "beginner":
            exp_factor = 0.85
        elif experience == "intermediate":
            exp_factor = 1.0
        elif experience == "advanced":
            exp_factor = 1.12
        else:  # elite
            exp_factor = 1.25

        if activity in ("low", "sedentary"):
            activity_factor = 0.9
        elif activity in ("moderate", "normal"):
            activity_factor = 1.0
        else:
            activity_factor = 1.1

        if workouts_per_week <= 2:
            freq_factor = 1.1
        elif workouts_per_week <= 4:
            freq_factor = 1.0
        else:
            freq_factor = 0.9

        if strength_index <= 0:
            strength_factor = 0.9
        elif strength_index < 20:
            strength_factor = 1.0
        elif strength_index < 50:
            strength_factor = 1.12
        else:
            strength_factor = 1.25

        user_capacity = (
            age_factor
            * sex_factor
            * bmi_factor
            * exp_factor
            * activity_factor
            * freq_factor
            * strength_factor
        )

        for se in session.exercises:
            ex = Exercise.query.get(se.exercise_id)
            if not ex:
                continue

            primary = ex.muscles_primary or []
            secondary = ex.muscles_secondary or []

            sets = se.sets_done or se.sets_planned or 0

            reps_raw = se.reps_done or se.reps_planned or "0"
            try:
                reps = int(str(reps_raw).split("-")[0])
            except:
                reps = 0

            load = se.load_done or se.load_planned or 0

            import math

            if load <= 0:
                load_factor = 1.0 + (ex.difficulty * 0.3)
            else:
                load_factor = math.log(load + 1.0, 10) * (1.0 + ex.difficulty * 0.5)

            base_volume = sets * max(reps, 0)

            if load <= 0:
                intensity_factor = (reps / (reps + 10.0)) * 0.8 if reps > 0 else 0.3
            else:
                intensity_factor = (load / (load + reps + 10.0)) + (
                    reps / (reps + 20.0)
                )

            mp = ex.movement_pattern or "other"
            if mp == "upper-body":
                mp_factor = 1.0
            elif mp == "lower-body":
                mp_factor = 1.15
            elif mp == "core":
                mp_factor = 0.9
            elif mp == "mobility":
                mp_factor = 0.4
            elif mp == "full-body":
                mp_factor = 1.25
            else:
                mp_factor = 1.0

            risk_factor = 1.0 + (ex.risk_level * 0.05)

            exercise_raw = (
                base_volume * load_factor * intensity_factor * mp_factor * risk_factor
            )

            exercise_load = exercise_raw * user_capacity
            total_load += exercise_load

            if primary:
                per_primary = exercise_load * 0.7 / len(primary)
                for m in primary:
                    muscle_loads[m] = muscle_loads.get(m, 0.0) + per_primary

            if secondary:
                per_secondary = exercise_load * 0.3 / len(secondary)
                for m in secondary:
                    muscle_loads[m] = muscle_loads.get(m, 0.0) + per_secondary

        session.muscle_loads = muscle_loads
        return total_load

    @staticmethod
    def update_training_load_from_session(session, user):
        from myapp.app.training_engine.models.performance_state import PerformanceState

        total_load = TrainingSessionService._compute_session_load(session)

        if not user.performance_state:
            ps = PerformanceState(
                training_load=total_load,
                weight=user.weight,
            )
            db.session.add(ps)
            db.session.flush()
            user.performance_state_id = ps.id
        else:
            ps = user.performance_state
            ps.training_load = (ps.training_load or 0) + total_load

        db.session.commit()

    @staticmethod
    def finish_session(session, fatigue_after=None):
        from datetime import datetime

        session.status = "finished"
        session.finished_at = datetime.utcnow()
        session.fatigue_after = fatigue_after

        rpes = [se.rpe for se in session.exercises if se.rpe is not None]
        session.rpe_avg = sum(rpes) / len(rpes) if rpes else None

        db.session.commit()
        TrainingSessionService.update_training_load_from_session(session, session.user)
        return session
