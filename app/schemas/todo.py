from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import Priority


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    priority: Priority = Priority.MEDIUM
    due_date: datetime | None = None


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool | None = None
    priority: Priority | None = None
    due_date: datetime | None = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    priority: Priority
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime
    user_id: int

    model_config = {"from_attributes": True}


class TodoListResponse(BaseModel):
    items: list[TodoResponse]
    total: int
    page: int
    per_page: int
    pages: int
