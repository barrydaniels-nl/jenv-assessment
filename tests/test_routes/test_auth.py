

class TestRegister:
    def test_register_success(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_email(self, client, test_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "differentuser",
                "password": "password123",
            },
        )

        assert response.status_code == 409
        data = response.get_json()
        assert data["error"] == "conflict"
        assert "email" in data["message"].lower()

    def test_register_duplicate_username(self, client, test_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "different@example.com",
                "username": test_user.username,
                "password": "password123",
            },
        )

        assert response.status_code == 409
        data = response.get_json()
        assert data["error"] == "conflict"
        assert "username" in data["message"].lower()

    def test_register_invalid_email(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "username": "validuser",
                "password": "password123",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "validation_error"

    def test_register_password_too_short(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "valid@example.com",
                "username": "validuser",
                "password": "short",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "validation_error"

    def test_register_username_too_short(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "valid@example.com",
                "username": "ab",
                "password": "password123",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "validation_error"


class TestLogin:
    def test_login_success(self, client, test_user, test_user_password):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": test_user_password,
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "unauthorized"

    def test_login_nonexistent_email(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "unauthorized"

    def test_login_invalid_email_format(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid-email",
                "password": "password123",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "validation_error"


class TestRefresh:
    def test_refresh_success(self, client, refresh_headers):
        response = client.post(
            "/api/v1/auth/refresh",
            headers=refresh_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_without_token(self, client):
        response = client.post("/api/v1/auth/refresh")

        assert response.status_code == 401

    def test_refresh_with_access_token(self, client, auth_headers):
        response = client.post(
            "/api/v1/auth/refresh",
            headers=auth_headers,
        )

        # flask-jwt-extended returns 401 when wrong token type is used
        assert response.status_code == 401

    def test_refresh_invalid_token(self, client):
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401


class TestMe:
    def test_me_success(self, client, auth_headers, test_user):
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["is_active"] is True
        assert "password" not in data
        assert "password_hash" not in data

    def test_me_without_token(self, client):
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_me_invalid_token(self, client):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401
