from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.todo import Todo


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, min_length=3, max_length=100)
    password_hash: str = Field(max_length=255)
    is_active: bool = Field(default=True)

    todos: list["Todo"] = Relationship(back_populates="user")
