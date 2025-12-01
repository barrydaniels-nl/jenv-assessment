from typing import Any

from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: list[dict[str, Any]] | dict[str, Any] | None = None
