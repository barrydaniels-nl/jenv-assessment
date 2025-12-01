from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from sqlmodel import Session

from app.core.database import engine
from app.schemas import ErrorResponse, MessageResponse, TodoCreate, TodoResponse, TodoUpdate
from app.services.todo_service import (
    create_todo,
    delete_todo,
    get_todo,
    list_todos,
    toggle_todo,
    update_todo,
)

todos_bp = Blueprint("todos", __name__, url_prefix="/todos")


@todos_bp.route("", methods=["GET"])
@jwt_required()
def list_todos_route():
    user_id = int(get_jwt_identity())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    completed = request.args.get("completed", type=str)

    # Validate pagination
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 1
    if per_page > 100:
        per_page = 100

    # Parse completed filter
    completed_filter = None
    if completed is not None:
        completed_filter = completed.lower() in ("true", "1", "yes")

    with Session(engine) as session:
        result = list_todos(session, user_id, page, per_page, completed_filter)
        return jsonify(result.model_dump())


@todos_bp.route("", methods=["POST"])
@jwt_required()
def create_todo_route():
    user_id = int(get_jwt_identity())

    try:
        data = TodoCreate.model_validate(request.get_json())
    except ValidationError as e:
        return (
            jsonify(
                ErrorResponse(
                    error="validation_error",
                    message="Validation failed",
                    details=e.errors(),
                ).model_dump()
            ),
            400,
        )

    with Session(engine) as session:
        todo = create_todo(session, user_id, data)
        return jsonify(TodoResponse.model_validate(todo).model_dump()), 201


@todos_bp.route("/<int:todo_id>", methods=["GET"])
@jwt_required()
def get_todo_route(todo_id: int):
    user_id = int(get_jwt_identity())

    with Session(engine) as session:
        todo = get_todo(session, todo_id, user_id)
        if todo is None:
            return (
                jsonify(
                    ErrorResponse(
                        error="not_found",
                        message="Todo not found",
                    ).model_dump()
                ),
                404,
            )

        return jsonify(TodoResponse.model_validate(todo).model_dump())


@todos_bp.route("/<int:todo_id>", methods=["PUT"])
@jwt_required()
def update_todo_route(todo_id: int):
    user_id = int(get_jwt_identity())

    try:
        data = TodoUpdate.model_validate(request.get_json())
    except ValidationError as e:
        return (
            jsonify(
                ErrorResponse(
                    error="validation_error",
                    message="Validation failed",
                    details=e.errors(),
                ).model_dump()
            ),
            400,
        )

    with Session(engine) as session:
        todo = update_todo(session, todo_id, user_id, data)
        if todo is None:
            return (
                jsonify(
                    ErrorResponse(
                        error="not_found",
                        message="Todo not found",
                    ).model_dump()
                ),
                404,
            )

        return jsonify(TodoResponse.model_validate(todo).model_dump())


@todos_bp.route("/<int:todo_id>", methods=["DELETE"])
@jwt_required()
def delete_todo_route(todo_id: int):
    user_id = int(get_jwt_identity())

    with Session(engine) as session:
        success = delete_todo(session, todo_id, user_id)
        if not success:
            return (
                jsonify(
                    ErrorResponse(
                        error="not_found",
                        message="Todo not found",
                    ).model_dump()
                ),
                404,
            )

        return jsonify(MessageResponse(message="Todo deleted successfully").model_dump())


@todos_bp.route("/<int:todo_id>/toggle", methods=["POST"])
@jwt_required()
def toggle_todo_route(todo_id: int):
    user_id = int(get_jwt_identity())

    with Session(engine) as session:
        todo = toggle_todo(session, todo_id, user_id)
        if todo is None:
            return (
                jsonify(
                    ErrorResponse(
                        error="not_found",
                        message="Todo not found",
                    ).model_dump()
                ),
                404,
            )

        return jsonify(TodoResponse.model_validate(todo).model_dump())
