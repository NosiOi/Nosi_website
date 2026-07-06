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
        total = 0

        for se in session.exercises:
            ex = Exercise.query.get(se.exercise_id)
            if not ex:
                continue

            primary_muscles = ex.muscles_primary or []
            secondary_muscles = ex.muscles_secondary or []

            primary = len(primary_muscles)
            secondary = len(secondary_muscles)

            sets = se.sets_done or se.sets_planned or 0
            reps_raw = se.reps_done or se.reps_planned or "0"
            try:
                reps = int(str(reps_raw).split("-")[0])
            except Exception:
                reps = 0

            load = se.load_done or se.load_planned or 0
            rpe = se.rpe or 6

            muscle_factor = primary * 1.0 + secondary * 0.5
            difficulty_factor = ex.difficulty * 0.8 + 1.0

            if load > 0:
                intensity_factor = (load / (load + reps + 1)) * 1.2
            else:
                intensity_factor = (reps / (reps + 10)) * 0.8

            rpe_factor = (rpe / 10) ** 1.3

            volume = sets * reps * (load + 1)

            exercise_load = (
                volume
                * muscle_factor
                * difficulty_factor
                * intensity_factor
                * rpe_factor
            )
            total += exercise_load

        return total

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
