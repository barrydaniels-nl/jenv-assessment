import os

import pytest

# Set test database before importing app modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture
def app():
    from sqlmodel import SQLModel

    from app import create_app
    from app.core.database import engine

    test_app = create_app()
    test_app.config["TESTING"] = True

    with test_app.app_context():
        SQLModel.metadata.create_all(engine)
        yield test_app
        SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def session(app):
    from sqlmodel import Session

    from app.core.database import engine

    with Session(engine) as sess:
        yield sess


@pytest.fixture
def test_user(app, session):
    from app.models import User
    from app.services.auth_service import hash_password

    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=hash_password("password123"),
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_user_password():
    return "password123"


@pytest.fixture
def second_user(app, session):
    from app.models import User
    from app.services.auth_service import hash_password

    user = User(
        email="second@example.com",
        username="seconduser",
        password_hash=hash_password("password456"),
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def auth_headers(app, test_user):
    from flask_jwt_extended import create_access_token

    with app.app_context():
        token = create_access_token(identity=str(test_user.id))
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def refresh_headers(app, test_user):
    from flask_jwt_extended import create_refresh_token

    with app.app_context():
        token = create_refresh_token(identity=str(test_user.id))
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user_auth_headers(app, second_user):
    from flask_jwt_extended import create_access_token

    with app.app_context():
        token = create_access_token(identity=str(second_user.id))
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_todo(app, session, test_user):
    from app.models import Todo
    from app.models.enums import Priority

    todo = Todo(
        title="Test Todo",
        description="Test description",
        priority=Priority.MEDIUM,
        user_id=test_user.id,
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
