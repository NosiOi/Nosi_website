from myapp.app.training_engine.models.exercise import Exercise
from myapp.app.models.training_session import TrainingSession
from myapp.app.models.performance_state import PerformanceState
import datetime as dt


class RecommendationEngineService:
    def __init__(self, user):
        self.user = user

    def _load_sessions(self, days=90):
        today = dt.date.today()
        start = today - dt.timedelta(days=days)
        return TrainingSession.query.filter(
            TrainingSession.user_id == self.user.id,
            TrainingSession.started_at >= dt.datetime.combine(start, dt.time.min),
            TrainingSession.started_at <= dt.datetime.combine(today, dt.time.max),
        ).all()

    def _compute_muscle_loads(self, days=90):
        sessions = self._load_sessions(days=days)
        loads = {}
        for s in sessions:
            for se in s.exercises:
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
                load_val = se.load_done or se.load_planned or 0
                base = sets * max(reps, 0)
                total = base * (1 + (load_val or 0) / 100.0)
                if primary:
                    per = total * 0.7 / len(primary)
                    for m in primary:
                        loads[m] = loads.get(m, 0.0) + per
                if secondary:
                    per = total * 0.3 / len(secondary)
                    for m in secondary:
                        loads[m] = loads.get(m, 0.0) + per
        return loads

    def compute_weak_muscle_groups(self):
        loads = self._compute_muscle_loads(days=90)
        if not loads:
            return []
        values = list(loads.values())
        avg = sum(values) / len(values)
        weak = []
        for muscle, val in loads.items():
            if val < avg * 0.6:
                weak.append(muscle)
        weak_sorted = sorted(weak, key=lambda m: loads.get(m, 0.0))
        return weak_sorted

    def compute_exercise_recommendations(self, weak_muscles):
        if not weak_muscles:
            return []
        exercises = Exercise.query.all()
        recs = []
        used_ids = set()
        for muscle in weak_muscles:
            for ex in exercises:
                primary = ex.muscles_primary or []
                secondary = ex.muscles_secondary or []
                if muscle in primary or muscle in secondary:
                    if ex.id in used_ids:
                        continue
                    recs.append(ex.name)
                    used_ids.add(ex.id)
        return recs

    def compute_muscle_balance(self):
        loads = self._compute_muscle_loads(days=90)
        if not loads:
            return []

        def sum_groups(groups):
            return sum(loads.get(g, 0) for g in groups)

        chest = sum_groups(["chest"])
        back = sum_groups(["back"])
        quads = sum_groups(["quads"])
        hams = sum_groups(["hamstrings"])
        push = sum_groups(["chest", "shoulders", "triceps"])
        pull = sum_groups(["back", "biceps"])
        core = sum_groups(["abs", "obliques", "lower_back"])
        total = sum(loads.values()) or 1

        recs = []

        if chest < back * 0.7:
            recs.append("Груди тренуються значно менше ніж спина")
        if back < chest * 0.7:
            recs.append("Спина тренується значно менше ніж груди")
        if quads < hams * 0.7:
            recs.append("Квадрицепси відстають від задньої поверхні стегна")
        if hams < quads * 0.7:
            recs.append("Задня поверхня стегна відстає від квадрицепсів")
        if push < pull * 0.7:
            recs.append("Push-навантаження значно нижче ніж Pull")
        if pull < push * 0.7:
            recs.append("Pull-навантаження значно нижче ніж Push")
        if core < total * 0.1:
            recs.append("Кор отримує дуже мало навантаження")

        return recs

    def compute_strength_progress(self):
        history = (
            PerformanceState.query.filter_by(user_id=self.user.id)
            .order_by(PerformanceState.created_at.asc())
            .all()
        )
        if len(history) < 2:
            return []

        first = history[0]
        last = history[-1]

        def prog(a, b):
            if a == 0:
                return 0
            return (b - a) / a

        p_push = prog(first.pushups, last.pushups)
        p_squat = prog(first.squats, last.squats)
        p_sit = prog(first.situps, last.situps)

        recs = []

        if p_push < 0.05:
            recs.append("Прогрес сили грудей майже відсутній")
        if p_squat < 0.05:
            recs.append("Прогрес сили ніг майже відсутній")
        if p_sit < 0.05:
            recs.append("Прогрес сили кора майже відсутній")

        return recs
