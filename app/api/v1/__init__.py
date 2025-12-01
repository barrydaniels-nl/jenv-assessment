from flask import Blueprint

from app.api.v1.routes.auth import auth_bp
from app.api.v1.routes.health import health_bp
from app.api.v1.routes.todos import todos_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/api/v1")

v1_bp.register_blueprint(health_bp)
v1_bp.register_blueprint(auth_bp)
v1_bp.register_blueprint(todos_bp)
