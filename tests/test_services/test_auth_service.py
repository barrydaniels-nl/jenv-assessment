from app.schemas import UserRegister
from app.services.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    hash_password,
    verify_password,
)


class TestPasswordFunctions:
    def test_hash_password_returns_bcrypt_hash(self):
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_hash_password_different_salts(self):
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False


class TestGetUserById:
    def test_get_user_by_id_exists(self, app, session, test_user):
        user = get_user_by_id(session, test_user.id)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_by_id_not_found(self, app, session):
        user = get_user_by_id(session, 99999)

        assert user is None


class TestGetUserByEmail:
    def test_get_user_by_email_exists(self, app, session, test_user):
        user = get_user_by_email(session, test_user.email)

        assert user is not None
        assert user.email == test_user.email

    def test_get_user_by_email_not_found(self, app, session):
        user = get_user_by_email(session, "nonexistent@example.com")

        assert user is None


class TestGetUserByUsername:
    def test_get_user_by_username_exists(self, app, session, test_user):
        user = get_user_by_username(session, test_user.username)

        assert user is not None
        assert user.username == test_user.username

    def test_get_user_by_username_not_found(self, app, session):
        user = get_user_by_username(session, "nonexistent")

        assert user is None


class TestCreateUser:
    def test_create_user_success(self, app, session):
        data = UserRegister(
            email="newuser@example.com",
            username="newuser",
            password="password123",
        )

        user = create_user(session, data)

        assert user is not None
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.is_active is True

    def test_create_user_hashes_password(self, app, session):
        data = UserRegister(
            email="hashtest@example.com",
            username="hashtest",
            password="plainpassword",
        )

        user = create_user(session, data)

        assert user.password_hash != "plainpassword"
        assert user.password_hash.startswith("$2b$")
        assert verify_password("plainpassword", user.password_hash) is True


class TestAuthenticateUser:
    def test_authenticate_user_success(
        self, app, session, test_user, test_user_password
    ):
        user = authenticate_user(session, test_user.email, test_user_password)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_authenticate_user_wrong_password(self, app, session, test_user):
        user = authenticate_user(session, test_user.email, "wrongpassword")

        assert user is None

    def test_authenticate_user_nonexistent_email(self, app, session):
        user = authenticate_user(session, "nonexistent@example.com", "password123")

        assert user is None
