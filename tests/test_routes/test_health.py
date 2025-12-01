class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/api/v1/health")

        assert response.status_code == 200

    def test_health_response_format(self, client):
        response = client.get("/api/v1/health")
        data = response.get_json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
        assert data["service"] == "flask-todo-api"
