from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import date as Date, datetime


# ── Auth ──────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    username: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    email: str
    username: Optional[str]
    created_at: datetime
    class Config: from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


# ── Subjects ──────────────────────────────────────────────────────────────────
class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = "#1d9bf0"

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class Subject(BaseModel):
    id: int; user_id: int; name: str; color: str; created_at: datetime
    class Config: from_attributes = True


# ── Homework ──────────────────────────────────────────────────────────────────
class HomeworkCreate(BaseModel):
    subject_id: int
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    due_date: Optional[Date] = None
    priority: Optional[Literal["low","medium","high"]] = "medium"

class HomeworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[Date] = None
    completed: Optional[bool] = None
    priority: Optional[Literal["low","medium","high"]] = None

class Homework(BaseModel):
    id: int; user_id: int; subject_id: int; title: str
    description: Optional[str]; due_date: Optional[Date]
    completed: bool; priority: str; created_at: datetime
    subject_name: Optional[str] = None; subject_color: Optional[str] = None
    class Config: from_attributes = True


# ── Exams ─────────────────────────────────────────────────────────────────────
class ExamCreate(BaseModel):
    subject_id: int
    title: str = Field(..., min_length=1)
    type: Optional[Literal["exam","test","presentation"]] = "exam"
    date: Optional[Date] = None
    description: Optional[str] = None

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[Literal["exam","test","presentation"]] = None
    date: Optional[Date] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Exam(BaseModel):
    id: int; user_id: int; subject_id: int; title: str; type: str
    date: Optional[Date]; description: Optional[str]; completed: bool; created_at: datetime
    subject_name: Optional[str] = None; subject_color: Optional[str] = None
    class Config: from_attributes = True


# ── Grades ────────────────────────────────────────────────────────────────────
class GradeCreate(BaseModel):
    subject_id: int
    title: str = Field(..., min_length=1)
    score: float = Field(..., ge=0, le=15)
    weight: Optional[float] = Field(1.0, ge=0.1, le=10)
    date: Optional[Date] = None

class GradeUpdate(BaseModel):
    title: Optional[str] = None
    score: Optional[float] = Field(None, ge=0, le=15)
    weight: Optional[float] = None
    date: Optional[Date] = None

class Grade(BaseModel):
    id: int; user_id: int; subject_id: int; title: str
    score: float; weight: float; date: Optional[Date]; created_at: datetime
    subject_name: Optional[str] = None; subject_color: Optional[str] = None
    class Config: from_attributes = True

class SubjectAverage(BaseModel):
    subject_id: int; subject_name: str; subject_color: str
    average: float; grade_count: int; highest: float; lowest: float


# ── Calendar ──────────────────────────────────────────────────────────────────
class CalendarEventCreate(BaseModel):
    title: str = Field(..., min_length=1)
    date: Date
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    type: Optional[Literal["study","exam","other"]] = "study"
    subject_id: Optional[int] = None
    color: Optional[str] = None

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[Date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    type: Optional[str] = None
    subject_id: Optional[int] = None
    color: Optional[str] = None

class CalendarEvent(BaseModel):
    id: int; user_id: int; title: str; date: Date
    start_time: Optional[str]; end_time: Optional[str]
    type: str; subject_id: Optional[int]; color: Optional[str]; created_at: datetime
    subject_name: Optional[str] = None
    class Config: from_attributes = True


# ── Dashboard ─────────────────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    homework_pending: int
    homework_overdue: int
    exams_upcoming: int
    overall_average: float
    total_grades: int
