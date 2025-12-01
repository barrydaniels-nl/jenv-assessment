import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

from app.api.v1 import v1_bp
from app.core.config import Config
from app.schemas import ErrorResponse

jwt = JWTManager()
cors = CORS()

SWAGGER_URL = "/docs"
API_URL = "/openapi.yaml"

# Get the project root directory (parent of app/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)

    # Configuration
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_ACCESS_TOKEN_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = Config.JWT_REFRESH_TOKEN_EXPIRES

    # Initialize extensions
    jwt.init_app(app)
    cors.init_app(app, origins=Config.get_cors_origins())

    # Swagger UI
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={"app_name": "Flask TODO API"},
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Serve OpenAPI spec
    @app.route("/openapi.yaml")
    def serve_openapi():
        return send_from_directory(ROOT_DIR, "openapi.yaml")

    # Register blueprints
    app.register_blueprint(v1_bp)

    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(error_message):
        return (
            jsonify(
                ErrorResponse(
                    error="unauthorized",
                    message="Missing or invalid authorization header",
                ).model_dump()
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error_message):
        return (
            jsonify(
                ErrorResponse(
                    error="unauthorized",
                    message="Invalid token",
                ).model_dump()
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                ErrorResponse(
                    error="unauthorized",
                    message="Token has expired",
                ).model_dump()
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                ErrorResponse(
                    error="unauthorized",
                    message="Token has been revoked",
                ).model_dump()
            ),
            401,
        )

    return app
