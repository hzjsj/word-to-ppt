from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TaskType = Literal["preprocess", "ppt", "knowledge"]
TaskStatus = Literal["pending", "running", "done", "failed"]


class TaskCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    task_type: TaskType
    options: list[str] = Field(default_factory=list)
    message: str | None = Field(default=None, max_length=2000)


class TaskUpdate(BaseModel):
    status: TaskStatus | None = None
    result_path: str | None = Field(default=None, max_length=500)
    message: str | None = Field(default=None, max_length=2000)


class EventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=50)
    detail: str | None = Field(default=None, max_length=2000)


class TaskEventOut(BaseModel):
    id: int
    task_id: int
    event_type: str
    detail: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskOut(BaseModel):
    id: int
    filename: str
    task_type: str
    options: list[str] = Field(default_factory=list)
    status: str
    result_path: str | None
    message: str | None
    created_at: datetime
    updated_at: datetime
    events: list[TaskEventOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
