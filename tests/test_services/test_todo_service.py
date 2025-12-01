from datetime import datetime, timezone

from app.models import Todo
from app.models.enums import Priority
from app.schemas import TodoCreate, TodoUpdate
from app.services.todo_service import (
    create_todo,
    delete_todo,
    get_todo,
    list_todos,
    toggle_todo,
    update_todo,
)


class TestCreateTodo:
    def test_create_todo_success(self, app, session, test_user):
        data = TodoCreate(title="New Todo")

        todo = create_todo(session, test_user.id, data)

        assert todo is not None
        assert todo.id is not None
        assert todo.title == "New Todo"
        assert todo.user_id == test_user.id

    def test_create_todo_with_all_fields(self, app, session, test_user):
        due_date = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        data = TodoCreate(
            title="Full Todo",
            description="A complete todo with all fields",
            priority=Priority.HIGH,
            due_date=due_date,
        )

        todo = create_todo(session, test_user.id, data)

        assert todo.title == "Full Todo"
        assert todo.description == "A complete todo with all fields"
        assert todo.priority == Priority.HIGH
        # SQLite doesn't preserve timezone info, so compare without timezone
        assert todo.due_date.replace(tzinfo=timezone.utc) == due_date

    def test_create_todo_default_values(self, app, session, test_user):
        data = TodoCreate(title="Minimal Todo")

        todo = create_todo(session, test_user.id, data)

        assert todo.description is None
        assert todo.completed is False
        assert todo.priority == Priority.MEDIUM
        assert todo.due_date is None
        assert todo.created_at is not None
        assert todo.updated_at is not None


class TestGetTodo:
    def test_get_todo_success(self, app, session, test_user, test_todo):
        todo = get_todo(session, test_todo.id, test_user.id)

        assert todo is not None
        assert todo.id == test_todo.id
        assert todo.title == test_todo.title

    def test_get_todo_not_found(self, app, session, test_user):
        todo = get_todo(session, 99999, test_user.id)

        assert todo is None

    def test_get_todo_wrong_user(self, app, session, test_todo, second_user):
        todo = get_todo(session, test_todo.id, second_user.id)

        assert todo is None


class TestListTodos:
    def test_list_todos_empty(self, app, session, test_user):
        result = list_todos(session, test_user.id)

        assert result.items == []
        assert result.total == 0
        assert result.page == 1
        assert result.per_page == 10
        assert result.pages == 1

    def test_list_todos_with_items(self, app, session, test_user):
        for i in range(3):
            todo = Todo(
                title=f"Todo {i}",
                user_id=test_user.id,
            )
            session.add(todo)
        session.commit()

        result = list_todos(session, test_user.id)

        assert len(result.items) == 3
        assert result.total == 3

    def test_list_todos_pagination(self, app, session, test_user):
        for i in range(15):
            todo = Todo(
                title=f"Todo {i}",
                user_id=test_user.id,
            )
            session.add(todo)
        session.commit()

        result = list_todos(session, test_user.id, page=1, per_page=5)

        assert len(result.items) == 5
        assert result.total == 15
        assert result.page == 1
        assert result.per_page == 5
        assert result.pages == 3

    def test_list_todos_pagination_page_2(self, app, session, test_user):
        for i in range(15):
            todo = Todo(
                title=f"Todo {i}",
                user_id=test_user.id,
            )
            session.add(todo)
        session.commit()

        result = list_todos(session, test_user.id, page=2, per_page=5)

        assert len(result.items) == 5
        assert result.page == 2

    def test_list_todos_filter_completed_true(self, app, session, test_user):
        todo1 = Todo(title="Completed", user_id=test_user.id, completed=True)
        todo2 = Todo(title="Not Completed", user_id=test_user.id, completed=False)
        session.add(todo1)
        session.add(todo2)
        session.commit()

        result = list_todos(session, test_user.id, completed=True)

        assert len(result.items) == 1
        assert result.items[0].completed is True
        assert result.total == 1

    def test_list_todos_filter_completed_false(self, app, session, test_user):
        todo1 = Todo(title="Completed", user_id=test_user.id, completed=True)
        todo2 = Todo(title="Not Completed", user_id=test_user.id, completed=False)
        session.add(todo1)
        session.add(todo2)
        session.commit()

        result = list_todos(session, test_user.id, completed=False)

        assert len(result.items) == 1
        assert result.items[0].completed is False
        assert result.total == 1

    def test_list_todos_user_isolation(self, app, session, test_user, second_user):
        todo1 = Todo(title="User 1 Todo", user_id=test_user.id)
        todo2 = Todo(title="User 2 Todo", user_id=second_user.id)
        session.add(todo1)
        session.add(todo2)
        session.commit()

        result = list_todos(session, test_user.id)

        assert len(result.items) == 1
        assert result.items[0].title == "User 1 Todo"


class TestUpdateTodo:
    def test_update_todo_success(self, app, session, test_user, test_todo):
        data = TodoUpdate(title="Updated Title", description="Updated description")

        todo = update_todo(session, test_todo.id, test_user.id, data)

        assert todo is not None
        assert todo.title == "Updated Title"
        assert todo.description == "Updated description"

    def test_update_todo_partial(self, app, session, test_user, test_todo):
        original_description = test_todo.description
        data = TodoUpdate(title="Only Title Updated")

        todo = update_todo(session, test_todo.id, test_user.id, data)

        assert todo is not None
        assert todo.title == "Only Title Updated"
        assert todo.description == original_description

    def test_update_todo_not_found(self, app, session, test_user):
        data = TodoUpdate(title="Updated")

        todo = update_todo(session, 99999, test_user.id, data)

        assert todo is None

    def test_update_todo_wrong_user(self, app, session, test_todo, second_user):
        data = TodoUpdate(title="Hacked")

        todo = update_todo(session, test_todo.id, second_user.id, data)

        assert todo is None

    def test_update_todo_updates_timestamp(self, app, session, test_user, test_todo):
        original_updated_at = test_todo.updated_at
        data = TodoUpdate(title="Timestamp Test")

        todo = update_todo(session, test_todo.id, test_user.id, data)

        assert todo.updated_at > original_updated_at


class TestDeleteTodo:
    def test_delete_todo_success(self, app, session, test_user, test_todo):
        result = delete_todo(session, test_todo.id, test_user.id)

        assert result is True

        deleted_todo = get_todo(session, test_todo.id, test_user.id)
        assert deleted_todo is None

    def test_delete_todo_not_found(self, app, session, test_user):
        result = delete_todo(session, 99999, test_user.id)

        assert result is False

    def test_delete_todo_wrong_user(self, app, session, test_todo, second_user):
        result = delete_todo(session, test_todo.id, second_user.id)

        assert result is False


class TestToggleTodo:
    def test_toggle_todo_to_completed(self, app, session, test_user, test_todo):
        assert test_todo.completed is False

        todo = toggle_todo(session, test_todo.id, test_user.id)

        assert todo is not None
        assert todo.completed is True

    def test_toggle_todo_to_uncompleted(self, app, session, test_user):
        completed_todo = Todo(
            title="Completed Todo",
            user_id=test_user.id,
            completed=True,
        )
        session.add(completed_todo)
        session.commit()
        session.refresh(completed_todo)

        todo = toggle_todo(session, completed_todo.id, test_user.id)

        assert todo is not None
        assert todo.completed is False

    def test_toggle_todo_not_found(self, app, session, test_user):
        todo = toggle_todo(session, 99999, test_user.id)

        assert todo is None

    def test_toggle_todo_wrong_user(self, app, session, test_todo, second_user):
        todo = toggle_todo(session, test_todo.id, second_user.id)

        assert todo is None

    def test_toggle_todo_updates_timestamp(self, app, session, test_user, test_todo):
        original_updated_at = test_todo.updated_at

        todo = toggle_todo(session, test_todo.id, test_user.id)

        assert todo.updated_at > original_updated_at
