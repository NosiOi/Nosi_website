from myapp.app import db
from myapp.app.models.training_session import TrainingSession, SessionExercise
from myapp.app.services.training_engine_service import TrainingEngineService


class TrainingSessionService:

    @staticmethod
    def start_session(user, fatigue_before: float | None = None):
        plan = TrainingEngineService.generate_plan(user, week=1)
        day = next(iter(plan.days.values()))

        session = TrainingSession(
            user_id=user.id,
            fatigue_before=fatigue_before,
            status="active",
        )
        db.session.add(session)
        db.session.flush()

        for ex in day.exercises:
            se = SessionExercise(
                session_id=session.id,
                exercise_id=ex["exercise"].id,
                sets_planned=ex["sets"],
                reps_planned=ex["reps"],
                load_planned=ex.get("load"),
            )
            db.session.add(se)

        db.session.commit()
        return session

    @staticmethod
    def update_exercise(session: TrainingSession, exercise_id: str, data: dict):
        se = SessionExercise.query.filter_by(
            session_id=session.id,
            exercise_id=exercise_id
        ).first()

        if not se:
            return None

        se.sets_done = data.get("sets_done", se.sets_done)
        se.reps_done = data.get("reps_done", se.reps_done)
        se.load_done = data.get("load_done", se.load_done)
        se.rpe = data.get("rpe", se.rpe)

        db.session.commit()
        return se

    @staticmethod
    def finish_session(session: TrainingSession, fatigue_after: float | None = None):
        from datetime import datetime

        session.status = "finished"
        session.finished_at = datetime.utcnow()
        session.fatigue_after = fatigue_after

        rpes = [se.rpe for se in session.exercises if se.rpe is not None]
        session.rpe_avg = sum(rpes) / len(rpes) if rpes else None

        db.session.commit()
        return session
