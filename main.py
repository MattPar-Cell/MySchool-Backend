from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession
from typing import Optional
from datetime import timedelta
import models, schemas, crud
from database import SessionLocal, engine
from auth import hash_password, verify_password, create_access_token, get_current_user, get_db
from config import ACCESS_TOKEN_EXPIRE_MINUTES

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MySchool API", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=schemas.TokenResponse, tags=["Auth"])
def register(payload: schemas.RegisterRequest, db: DBSession = Depends(get_db)):
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, payload.email, hash_password(payload.password), payload.username)
    token = create_access_token(user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return schemas.TokenResponse(access_token=token, user=schemas.UserPublic.model_validate(user))

@app.post("/auth/login", response_model=schemas.TokenResponse, tags=["Auth"])
def login(payload: schemas.LoginRequest, db: DBSession = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return schemas.TokenResponse(access_token=token, user=schemas.UserPublic.model_validate(user))

@app.get("/auth/me", response_model=schemas.UserPublic, tags=["Auth"])
def me(current_user=Depends(get_current_user)):
    return current_user


# ── Dashboard ──────────────────────────────────────────────────────────────────
@app.get("/dashboard", response_model=schemas.DashboardStats, tags=["Dashboard"])
def dashboard(current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.get_dashboard_stats(db, current_user.id)


# ── Subjects ──────────────────────────────────────────────────────────────────
@app.get("/subjects", response_model=list[schemas.Subject], tags=["Subjects"])
def list_subjects(current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.get_subjects(db, current_user.id)

@app.post("/subjects", response_model=schemas.Subject, status_code=201, tags=["Subjects"])
def create_subject(payload: schemas.SubjectCreate, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.create_subject(db, current_user.id, payload)

@app.put("/subjects/{subject_id}", response_model=schemas.Subject, tags=["Subjects"])
def update_subject(subject_id: int, payload: schemas.SubjectUpdate, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    s = crud.update_subject(db, current_user.id, subject_id, payload)
    if not s: raise HTTPException(404, "Subject not found")
    return s

@app.delete("/subjects/{subject_id}", status_code=204, tags=["Subjects"])
def delete_subject(subject_id: int, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    if not crud.delete_subject(db, current_user.id, subject_id): raise HTTPException(404, "Not found")


# ── Homework ──────────────────────────────────────────────────────────────────
@app.get("/homework", response_model=list[schemas.Homework], tags=["Homework"])
def list_homework(completed: Optional[bool] = Query(None), current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.get_homework(db, current_user.id, completed)

@app.post("/homework", response_model=schemas.Homework, status_code=201, tags=["Homework"])
def create_homework(payload: schemas.HomeworkCreate, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.create_homework(db, current_user.id, payload)

@app.patch("/homework/{hw_id}", response_model=schemas.Homework, tags=["Homework"])
def update_homework(hw_id: int, payload: schemas.HomeworkUpdate, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    h = crud.update_homework(db, current_user.id, hw_id, payload)
    if not h: raise HTTPException(404, "Not found")
    return h

@app.delete("/homework/{hw_id}", status_code=204, tags=["Homework"])
def delete_homework(hw_id: int, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    if not crud.delete_homework(db, current_user.id, hw_id): raise HTTPException(404, "Not found")


# ── Exams ─────────────────────────────────────────────────────────────────────
@app.get("/exams", response_model=list[schemas.Exam], tags=["Exams"])
def list_exams(completed: Optional[bool] = Query(None), current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.get_exams(db, current_user.id, completed)

@app.post("/exams", response_model=schemas.Exam, status_code=201, tags=["Exams"])
def create_exam(payload: schemas.ExamCreate, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.create_exam(db, current_user.id, payload)

@app.patch("/exams/{exam_id}", response_model=schemas.Exam, tags=["Exams"])
def update_exam(exam_id: int, payload: schemas.ExamUpdate, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    e = crud.update_exam(db, current_user.id, exam_id, payload)
    if not e: raise HTTPException(404, "Not found")
    return e

@app.delete("/exams/{exam_id}", status_code=204, tags=["Exams"])
def delete_exam(exam_id: int, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    if not crud.delete_exam(db, current_user.id, exam_id): raise HTTPException(404, "Not found")


# ── Grades ────────────────────────────────────────────────────────────────────
@app.get("/grades", response_model=list[schemas.Grade], tags=["Grades"])
def list_grades(subject_id: Optional[int] = Query(None), current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.get_grades(db, current_user.id, subject_id)

@app.get("/grades/averages", response_model=list[schemas.SubjectAverage], tags=["Grades"])
def get_averages(current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.get_subject_averages(db, current_user.id)

@app.post("/grades", response_model=schemas.Grade, status_code=201, tags=["Grades"])
def create_grade(payload: schemas.GradeCreate, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.create_grade(db, current_user.id, payload)

@app.patch("/grades/{grade_id}", response_model=schemas.Grade, tags=["Grades"])
def update_grade(grade_id: int, payload: schemas.GradeUpdate, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    g = crud.update_grade(db, current_user.id, grade_id, payload)
    if not g: raise HTTPException(404, "Not found")
    return g

@app.delete("/grades/{grade_id}", status_code=204, tags=["Grades"])
def delete_grade(grade_id: int, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    if not crud.delete_grade(db, current_user.id, grade_id): raise HTTPException(404, "Not found")


# ── Calendar ──────────────────────────────────────────────────────────────────
@app.get("/calendar", response_model=list[schemas.CalendarEvent], tags=["Calendar"])
def list_calendar(month: Optional[int] = Query(None), year: Optional[int] = Query(None), current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.get_calendar_events(db, current_user.id, month, year)

@app.post("/calendar", response_model=schemas.CalendarEvent, status_code=201, tags=["Calendar"])
def create_calendar_event(payload: schemas.CalendarEventCreate, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    return crud.create_calendar_event(db, current_user.id, payload)

@app.patch("/calendar/{event_id}", response_model=schemas.CalendarEvent, tags=["Calendar"])
def update_calendar_event(event_id: int, payload: schemas.CalendarEventUpdate, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    e = crud.update_calendar_event(db, current_user.id, event_id, payload)
    if not e: raise HTTPException(404, "Not found")
    return e

@app.delete("/calendar/{event_id}", status_code=204, tags=["Calendar"])
def delete_calendar_event(event_id: int, current_user=Depends(get_current_user), db: DBSession = Depends(get_db)):
    if not crud.delete_calendar_event(db, current_user.id, event_id): raise HTTPException(404, "Not found")
