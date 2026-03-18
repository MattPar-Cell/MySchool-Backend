from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    email           = Column(String, unique=True, nullable=False, index=True)
    username        = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at      = Column(DateTime, server_default=func.now())

    subjects  = relationship("Subject",       back_populates="user", cascade="all, delete-orphan")
    homework  = relationship("Homework",      back_populates="user", cascade="all, delete-orphan")
    exams     = relationship("Exam",          back_populates="user", cascade="all, delete-orphan")
    grades    = relationship("Grade",         back_populates="user", cascade="all, delete-orphan")
    cal_events = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    name       = Column(String, nullable=False)
    color      = Column(String, default="#1d9bf0")
    created_at = Column(DateTime, server_default=func.now())

    user     = relationship("User", back_populates="subjects")
    homework = relationship("Homework",  back_populates="subject", cascade="all, delete-orphan")
    exams    = relationship("Exam",      back_populates="subject", cascade="all, delete-orphan")
    grades   = relationship("Grade",     back_populates="subject", cascade="all, delete-orphan")


class Homework(Base):
    __tablename__ = "homework"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id  = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title       = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date    = Column(Date, nullable=True)
    completed   = Column(Boolean, default=False)
    priority    = Column(String, default="medium")
    created_at  = Column(DateTime, server_default=func.now())

    user    = relationship("User",    back_populates="homework")
    subject = relationship("Subject", back_populates="homework")


class Exam(Base):
    __tablename__ = "exams"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id  = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title       = Column(String, nullable=False)
    type        = Column(String, default="exam")
    date        = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    completed   = Column(Boolean, default=False)
    created_at  = Column(DateTime, server_default=func.now())

    user    = relationship("User",    back_populates="exams")
    subject = relationship("Subject", back_populates="exams")


class Grade(Base):
    __tablename__ = "grades"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title      = Column(String, nullable=False)
    score      = Column(Float, nullable=False)
    weight     = Column(Float, default=1.0)
    date       = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user    = relationship("User",    back_populates="grades")
    subject = relationship("Subject", back_populates="grades")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    title      = Column(String, nullable=False)
    date       = Column(Date, nullable=False)
    start_time = Column(String, nullable=True)
    end_time   = Column(String, nullable=True)
    type       = Column(String, default="study")
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    color      = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="cal_events")
