from datetime import datetime, timezone

from sqlmodel import Session, func, select

from app.models import Todo
from app.schemas import TodoCreate, TodoListResponse, TodoResponse, TodoUpdate


def create_todo(session: Session, user_id: int, data: TodoCreate) -> Todo:
    todo = Todo(
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        user_id=user_id,
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def get_todo(session: Session, todo_id: int, user_id: int) -> Todo | None:
    statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    return session.exec(statement).first()


def list_todos(
    session: Session,
    user_id: int,
    page: int = 1,
    per_page: int = 10,
    completed: bool | None = None,
) -> TodoListResponse:
    # Base query
    statement = select(Todo).where(Todo.user_id == user_id)
    count_statement = (
        select(func.count()).select_from(Todo).where(Todo.user_id == user_id)
    )

    # Apply completed filter
    if completed is not None:
        statement = statement.where(Todo.completed == completed)
        count_statement = count_statement.where(Todo.completed == completed)

    # Get total count
    total = session.exec(count_statement).one()

    # Apply pagination
    offset = (page - 1) * per_page
    statement = (
        statement.offset(offset).limit(per_page).order_by(Todo.created_at.desc())
    )

    todos = session.exec(statement).all()
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    return TodoListResponse(
        items=[TodoResponse.model_validate(todo) for todo in todos],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


def update_todo(
    session: Session, todo_id: int, user_id: int, data: TodoUpdate
) -> Todo | None:
    todo = get_todo(session, todo_id, user_id)
    if todo is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)

    todo.updated_at = datetime.now(timezone.utc)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def delete_todo(session: Session, todo_id: int, user_id: int) -> bool:
    todo = get_todo(session, todo_id, user_id)
    if todo is None:
        return False

    session.delete(todo)
    session.commit()
    return True


def toggle_todo(session: Session, todo_id: int, user_id: int) -> Todo | None:
    todo = get_todo(session, todo_id, user_id)
    if todo is None:
        return None

    todo.completed = not todo.completed
    todo.updated_at = datetime.now(timezone.utc)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
