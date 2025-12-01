from app.models import Todo


class TestListTodos:
    def test_list_todos_empty(self, client, auth_headers):
        response = client.get("/api/v1/todos", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["per_page"] == 10

    def test_list_todos_with_items(self, client, auth_headers, test_todo):
        response = client.get("/api/v1/todos", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == test_todo.title

    def test_list_todos_pagination(self, client, auth_headers, session, test_user):
        for i in range(15):
            todo = Todo(title=f"Todo {i}", user_id=test_user.id)
            session.add(todo)
        session.commit()

        response = client.get(
            "/api/v1/todos?page=1&per_page=5",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 5
        assert data["total"] == 15
        assert data["pages"] == 3

    def test_list_todos_filter_completed(
        self, client, auth_headers, session, test_user
    ):
        todo1 = Todo(title="Completed", user_id=test_user.id, completed=True)
        todo2 = Todo(title="Not Completed", user_id=test_user.id, completed=False)
        session.add(todo1)
        session.add(todo2)
        session.commit()

        response = client.get(
            "/api/v1/todos?completed=true",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 1
        assert data["items"][0]["completed"] is True

    def test_list_todos_sort_by_title_asc(
        self, client, auth_headers, session, test_user
    ):
        todo1 = Todo(title="Zebra", user_id=test_user.id)
        todo2 = Todo(title="Apple", user_id=test_user.id)
        todo3 = Todo(title="Mango", user_id=test_user.id)
        session.add_all([todo1, todo2, todo3])
        session.commit()

        response = client.get(
            "/api/v1/todos?sort_by=title&order=asc",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        titles = [item["title"] for item in data["items"]]
        assert titles == ["Apple", "Mango", "Zebra"]

    def test_list_todos_sort_by_title_desc(
        self, client, auth_headers, session, test_user
    ):
        todo1 = Todo(title="Zebra", user_id=test_user.id)
        todo2 = Todo(title="Apple", user_id=test_user.id)
        todo3 = Todo(title="Mango", user_id=test_user.id)
        session.add_all([todo1, todo2, todo3])
        session.commit()

        response = client.get(
            "/api/v1/todos?sort_by=title&order=desc",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        titles = [item["title"] for item in data["items"]]
        assert titles == ["Zebra", "Mango", "Apple"]

    def test_list_todos_sort_by_priority(
        self, client, auth_headers, session, test_user
    ):
        from app.models.enums import Priority

        todo1 = Todo(title="Low", user_id=test_user.id, priority=Priority.LOW)
        todo2 = Todo(title="High", user_id=test_user.id, priority=Priority.HIGH)
        todo3 = Todo(title="Medium", user_id=test_user.id, priority=Priority.MEDIUM)
        session.add_all([todo1, todo2, todo3])
        session.commit()

        response = client.get(
            "/api/v1/todos?sort_by=priority&order=asc",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        priorities = [item["priority"] for item in data["items"]]
        # Sorts alphabetically: high, low, medium
        assert priorities == ["high", "low", "medium"]

    def test_list_todos_invalid_sort_field_falls_back(
        self, client, auth_headers, test_todo
    ):
        response = client.get(
            "/api/v1/todos?sort_by=invalid_field",
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_list_todos_invalid_order_falls_back(self, client, auth_headers, test_todo):
        response = client.get(
            "/api/v1/todos?order=invalid",
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_list_todos_unauthorized(self, client):
        response = client.get("/api/v1/todos")

        assert response.status_code == 401


class TestCreateTodo:
    def test_create_todo_success(self, client, auth_headers):
        response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "New Todo"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "New Todo"
        assert data["completed"] is False

    def test_create_todo_minimal(self, client, auth_headers):
        response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "Minimal"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "Minimal"
        assert data["description"] is None
        assert data["priority"] == "medium"

    def test_create_todo_all_fields(self, client, auth_headers):
        due_date = "2025-12-31T23:59:59Z"
        response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Full Todo",
                "description": "Complete description",
                "priority": "high",
                "due_date": due_date,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "Full Todo"
        assert data["description"] == "Complete description"
        assert data["priority"] == "high"
        assert data["due_date"] is not None

    def test_create_todo_invalid_priority(self, client, auth_headers):
        response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "Test", "priority": "invalid"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "validation_error"

    def test_create_todo_title_too_long(self, client, auth_headers):
        response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "x" * 201},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "validation_error"

    def test_create_todo_unauthorized(self, client):
        response = client.post(
            "/api/v1/todos",
            json={"title": "Test"},
        )

        assert response.status_code == 401


class TestGetTodo:
    def test_get_todo_success(self, client, auth_headers, test_todo):
        response = client.get(
            f"/api/v1/todos/{test_todo.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == test_todo.id
        assert data["title"] == test_todo.title

    def test_get_todo_not_found(self, client, auth_headers):
        response = client.get(
            "/api/v1/todos/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "not_found"

    def test_get_todo_wrong_user(self, client, second_user_auth_headers, test_todo):
        response = client.get(
            f"/api/v1/todos/{test_todo.id}",
            headers=second_user_auth_headers,
        )

        assert response.status_code == 404

    def test_get_todo_unauthorized(self, client, test_todo):
        response = client.get(f"/api/v1/todos/{test_todo.id}")

        assert response.status_code == 401


class TestUpdateTodo:
    def test_update_todo_success(self, client, auth_headers, test_todo):
        response = client.put(
            f"/api/v1/todos/{test_todo.id}",
            headers=auth_headers,
            json={"title": "Updated Title"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "Updated Title"

    def test_update_todo_partial(self, client, auth_headers, test_todo):
        original_title = test_todo.title
        response = client.put(
            f"/api/v1/todos/{test_todo.id}",
            headers=auth_headers,
            json={"description": "New description"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == original_title
        assert data["description"] == "New description"

    def test_update_todo_not_found(self, client, auth_headers):
        response = client.put(
            "/api/v1/todos/99999",
            headers=auth_headers,
            json={"title": "Updated"},
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "not_found"

    def test_update_todo_wrong_user(self, client, second_user_auth_headers, test_todo):
        response = client.put(
            f"/api/v1/todos/{test_todo.id}",
            headers=second_user_auth_headers,
            json={"title": "Hacked"},
        )

        assert response.status_code == 404

    def test_update_todo_unauthorized(self, client, test_todo):
        response = client.put(
            f"/api/v1/todos/{test_todo.id}",
            json={"title": "Updated"},
        )

        assert response.status_code == 401


class TestDeleteTodo:
    def test_delete_todo_success(self, client, auth_headers, test_todo):
        response = client.delete(
            f"/api/v1/todos/{test_todo.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data

        get_response = client.get(
            f"/api/v1/todos/{test_todo.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_todo_not_found(self, client, auth_headers):
        response = client.delete(
            "/api/v1/todos/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "not_found"

    def test_delete_todo_wrong_user(self, client, second_user_auth_headers, test_todo):
        response = client.delete(
            f"/api/v1/todos/{test_todo.id}",
            headers=second_user_auth_headers,
        )

        assert response.status_code == 404

    def test_delete_todo_unauthorized(self, client, test_todo):
        response = client.delete(f"/api/v1/todos/{test_todo.id}")

        assert response.status_code == 401


class TestToggleTodo:
    def test_toggle_todo_success(self, client, auth_headers, test_todo):
        assert test_todo.completed is False

        response = client.post(
            f"/api/v1/todos/{test_todo.id}/toggle",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["completed"] is True

    def test_toggle_todo_back(self, client, auth_headers, session, test_user):
        todo = Todo(title="Completed", user_id=test_user.id, completed=True)
        session.add(todo)
        session.commit()
        session.refresh(todo)

        response = client.post(
            f"/api/v1/todos/{todo.id}/toggle",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["completed"] is False

    def test_toggle_todo_not_found(self, client, auth_headers):
        response = client.post(
            "/api/v1/todos/99999/toggle",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "not_found"

    def test_toggle_todo_wrong_user(self, client, second_user_auth_headers, test_todo):
        response = client.post(
            f"/api/v1/todos/{test_todo.id}/toggle",
            headers=second_user_auth_headers,
        )

        assert response.status_code == 404

    def test_toggle_todo_unauthorized(self, client, test_todo):
        response = client.post(f"/api/v1/todos/{test_todo.id}/toggle")

        assert response.status_code == 401
