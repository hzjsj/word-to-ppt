import json

from sqlalchemy import desc
from sqlalchemy.orm import Session, selectinload

import models
import schemas


def _decode_options(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _to_task_out(task: models.DocumentTask) -> schemas.TaskOut:
    return schemas.TaskOut.model_validate(
        {
            **task.__dict__,
            "options": _decode_options(task.options),
            "events": task.events,
        }
    )


def create_task(db: Session, payload: schemas.TaskCreate) -> schemas.TaskOut:
    task = models.DocumentTask(
        filename=payload.filename,
        task_type=payload.task_type,
        options=json.dumps(payload.options, ensure_ascii=False),
        message=payload.message,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _to_task_out(task)


def list_tasks(db: Session, limit: int = 50) -> list[schemas.TaskOut]:
    tasks = (
        db.query(models.DocumentTask)
        .options(selectinload(models.DocumentTask.events))
        .order_by(desc(models.DocumentTask.created_at))
        .limit(limit)
        .all()
    )
    return [_to_task_out(task) for task in tasks]


def get_task(db: Session, task_id: int) -> schemas.TaskOut | None:
    task = (
        db.query(models.DocumentTask)
        .options(selectinload(models.DocumentTask.events))
        .filter(models.DocumentTask.id == task_id)
        .first()
    )
    return _to_task_out(task) if task else None


def update_task(db: Session, task_id: int, payload: schemas.TaskUpdate) -> schemas.TaskOut | None:
    task = db.query(models.DocumentTask).filter(models.DocumentTask.id == task_id).first()
    if not task:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    task = (
        db.query(models.DocumentTask)
        .options(selectinload(models.DocumentTask.events))
        .filter(models.DocumentTask.id == task_id)
        .first()
    )
    return _to_task_out(task) if task else None


def add_event(db: Session, task_id: int, payload: schemas.EventCreate) -> schemas.TaskEventOut | None:
    task = db.query(models.DocumentTask).filter(models.DocumentTask.id == task_id).first()
    if not task:
        return None

    event = models.TaskEvent(task_id=task_id, **payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return schemas.TaskEventOut.model_validate(event)
