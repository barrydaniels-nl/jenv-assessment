from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from pydantic import ValidationError
from sqlmodel import Session

from app.core.database import engine
from app.schemas import (
    ErrorResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = UserRegister.model_validate(request.get_json())
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
        # Check if email exists
        if get_user_by_email(session, data.email):
            return (
                jsonify(
                    ErrorResponse(
                        error="conflict",
                        message="Email already exists",
                    ).model_dump()
                ),
                409,
            )

        # Check if username exists
        if get_user_by_username(session, data.username):
            return (
                jsonify(
                    ErrorResponse(
                        error="conflict",
                        message="Username already exists",
                    ).model_dump()
                ),
                409,
            )

        user = create_user(session, data)
        return jsonify(UserResponse.model_validate(user).model_dump()), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = UserLogin.model_validate(request.get_json())
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
        user = authenticate_user(session, data.email, data.password)
        if user is None:
            return (
                jsonify(
                    ErrorResponse(
                        error="unauthorized",
                        message="Invalid credentials",
                    ).model_dump()
                ),
                401,
            )

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify(
            TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            ).model_dump()
        )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return jsonify(
        TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        ).model_dump()
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())

    with Session(engine) as session:
        user = get_user_by_id(session, user_id)
        if user is None:
            return (
                jsonify(
                    ErrorResponse(
                        error="not_found",
                        message="User not found",
                    ).model_dump()
                ),
                404,
            )

        return jsonify(UserResponse.model_validate(user).model_dump())
