from myapp.app.extensions import db
from myapp.app.models import User


def test_create_user(test_db):
    user = User(username="yarik", email="test@example.com", password="123456")
    db.session.add(user)
    db.session.commit()

    saved = User.query.filter_by(email="test@example.com").first()

    assert saved is not None
    assert saved.username == "yarik"
