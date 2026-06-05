from myapp.app.training_engine.models.user_profile_snapshot import UserProfileSnapshot


def test_user_profile_snapshot_creation():
    profile = UserProfileSnapshot(
        age=20,
        sex="male",
        weight=70,
        height=180,
        activity=1.6,
        goal="gain",
        experience="beginner",
        workouts_per_week=3,
        environment="gym",
        weak_points=["core"],
        strong_points=["chest"]
    )

    assert profile.age == 20
    assert profile.goal == "gain"
    assert "core" in profile.weak_points
