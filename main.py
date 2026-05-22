from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine, get_db

app = FastAPI(title="word-to-ppt API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    models.Base.metadata.create_all(bind=engine)


app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
def home() -> FileResponse:
    return FileResponse("frontend/index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tasks", response_model=schemas.TaskOut)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, payload)


@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    limit: int = Query(default=50, ge=1, le=500),
    status: schemas.TaskStatus | None = None,
    db: Session = Depends(get_db),
):
    tasks = crud.list_tasks(db, limit)
    if status:
        tasks = [task for task in tasks if task.status == status]
    return tasks


@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def patch_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = crud.update_task(db, task_id, payload)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks/{task_id}/events", response_model=schemas.TaskEventOut)
def create_event(task_id: int, payload: schemas.EventCreate, db: Session = Depends(get_db)):
    event = crud.add_event(db, task_id, payload)
    if not event:
        raise HTTPException(status_code=404, detail="Task not found")
    return event
