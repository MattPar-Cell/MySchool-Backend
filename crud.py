from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc
from datetime import date
import models, schemas


# ── Users ──────────────────────────────────────────────────────────────────────
def get_user_by_email(db: DBSession, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: DBSession, email: str, hashed_password: str, username: str = None):
    user = models.User(email=email, hashed_password=hashed_password, username=username)
    db.add(user); db.commit(); db.refresh(user)
    return user


# ── Subjects ──────────────────────────────────────────────────────────────────
def get_subjects(db: DBSession, user_id: int):
    return db.query(models.Subject).filter_by(user_id=user_id).order_by(models.Subject.name).all()

def create_subject(db: DBSession, user_id: int, payload: schemas.SubjectCreate):
    s = models.Subject(user_id=user_id, **payload.model_dump())
    db.add(s); db.commit(); db.refresh(s); return s

def update_subject(db: DBSession, user_id: int, subject_id: int, payload: schemas.SubjectUpdate):
    s = db.query(models.Subject).filter_by(id=subject_id, user_id=user_id).first()
    if not s: return None
    for k, v in payload.model_dump(exclude_none=True).items(): setattr(s, k, v)
    db.commit(); db.refresh(s); return s

def delete_subject(db: DBSession, user_id: int, subject_id: int):
    s = db.query(models.Subject).filter_by(id=subject_id, user_id=user_id).first()
    if not s: return False
    db.delete(s); db.commit(); return True


# ── Homework ──────────────────────────────────────────────────────────────────
def _enrich_hw(h):
    if h and h.subject:
        h.subject_name = h.subject.name; h.subject_color = h.subject.color
    return h

def get_homework(db: DBSession, user_id: int, completed=None):
    q = db.query(models.Homework).filter_by(user_id=user_id)
    if completed is not None: q = q.filter_by(completed=completed)
    return [_enrich_hw(h) for h in q.order_by(models.Homework.due_date).all()]

def create_homework(db: DBSession, user_id: int, payload: schemas.HomeworkCreate):
    h = models.Homework(user_id=user_id, **payload.model_dump())
    db.add(h); db.commit(); db.refresh(h); return _enrich_hw(h)

def update_homework(db: DBSession, user_id: int, hw_id: int, payload: schemas.HomeworkUpdate):
    h = db.query(models.Homework).filter_by(id=hw_id, user_id=user_id).first()
    if not h: return None
    for k, v in payload.model_dump(exclude_none=True).items(): setattr(h, k, v)
    db.commit(); db.refresh(h); return _enrich_hw(h)

def delete_homework(db: DBSession, user_id: int, hw_id: int):
    h = db.query(models.Homework).filter_by(id=hw_id, user_id=user_id).first()
    if not h: return False
    db.delete(h); db.commit(); return True


# ── Exams ─────────────────────────────────────────────────────────────────────
def _enrich_exam(e):
    if e and e.subject:
        e.subject_name = e.subject.name; e.subject_color = e.subject.color
    return e

def get_exams(db: DBSession, user_id: int, completed=None):
    q = db.query(models.Exam).filter_by(user_id=user_id)
    if completed is not None: q = q.filter_by(completed=completed)
    return [_enrich_exam(e) for e in q.order_by(models.Exam.date).all()]

def create_exam(db: DBSession, user_id: int, payload: schemas.ExamCreate):
    e = models.Exam(user_id=user_id, **payload.model_dump())
    db.add(e); db.commit(); db.refresh(e); return _enrich_exam(e)

def update_exam(db: DBSession, user_id: int, exam_id: int, payload: schemas.ExamUpdate):
    e = db.query(models.Exam).filter_by(id=exam_id, user_id=user_id).first()
    if not e: return None
    for k, v in payload.model_dump(exclude_none=True).items(): setattr(e, k, v)
    db.commit(); db.refresh(e); return _enrich_exam(e)

def delete_exam(db: DBSession, user_id: int, exam_id: int):
    e = db.query(models.Exam).filter_by(id=exam_id, user_id=user_id).first()
    if not e: return False
    db.delete(e); db.commit(); return True


# ── Grades ────────────────────────────────────────────────────────────────────
def _enrich_grade(g):
    if g and g.subject:
        g.subject_name = g.subject.name; g.subject_color = g.subject.color
    return g

def get_grades(db: DBSession, user_id: int, subject_id=None):
    q = db.query(models.Grade).filter_by(user_id=user_id)
    if subject_id: q = q.filter_by(subject_id=subject_id)
    return [_enrich_grade(g) for g in q.order_by(desc(models.Grade.date)).all()]

def create_grade(db: DBSession, user_id: int, payload: schemas.GradeCreate):
    g = models.Grade(user_id=user_id, **payload.model_dump())
    db.add(g); db.commit(); db.refresh(g); return _enrich_grade(g)

def update_grade(db: DBSession, user_id: int, grade_id: int, payload: schemas.GradeUpdate):
    g = db.query(models.Grade).filter_by(id=grade_id, user_id=user_id).first()
    if not g: return None
    for k, v in payload.model_dump(exclude_none=True).items(): setattr(g, k, v)
    db.commit(); db.refresh(g); return _enrich_grade(g)

def delete_grade(db: DBSession, user_id: int, grade_id: int):
    g = db.query(models.Grade).filter_by(id=grade_id, user_id=user_id).first()
    if not g: return False
    db.delete(g); db.commit(); return True

def get_subject_averages(db: DBSession, user_id: int):
    subjects = db.query(models.Subject).filter_by(user_id=user_id).all()
    result = []
    for s in subjects:
        grades = db.query(models.Grade).filter_by(subject_id=s.id, user_id=user_id).all()
        if not grades: continue
        total_weight = sum(g.weight for g in grades)
        avg = sum(g.score * g.weight for g in grades) / total_weight if total_weight else 0
        result.append(schemas.SubjectAverage(
            subject_id=s.id, subject_name=s.name, subject_color=s.color,
            average=round(avg, 2), grade_count=len(grades),
            highest=max(g.score for g in grades), lowest=min(g.score for g in grades)
        ))
    return result


# ── Calendar ──────────────────────────────────────────────────────────────────
def get_calendar_events(db: DBSession, user_id: int, month=None, year=None):
    q = db.query(models.CalendarEvent).filter_by(user_id=user_id)
    if month and year:
        from sqlalchemy import extract
        q = q.filter(extract('month', models.CalendarEvent.date) == month,
                     extract('year',  models.CalendarEvent.date) == year)
    events = q.order_by(models.CalendarEvent.date, models.CalendarEvent.start_time).all()
    for e in events:
        if e.subject_id:
            subj = db.query(models.Subject).filter_by(id=e.subject_id, user_id=user_id).first()
            if subj: e.subject_name = subj.name
    return events

def create_calendar_event(db: DBSession, user_id: int, payload: schemas.CalendarEventCreate):
    e = models.CalendarEvent(user_id=user_id, **payload.model_dump())
    db.add(e); db.commit(); db.refresh(e); return e

def update_calendar_event(db: DBSession, user_id: int, event_id: int, payload: schemas.CalendarEventUpdate):
    e = db.query(models.CalendarEvent).filter_by(id=event_id, user_id=user_id).first()
    if not e: return None
    for k, v in payload.model_dump(exclude_none=True).items(): setattr(e, k, v)
    db.commit(); db.refresh(e); return e

def delete_calendar_event(db: DBSession, user_id: int, event_id: int):
    e = db.query(models.CalendarEvent).filter_by(id=event_id, user_id=user_id).first()
    if not e: return False
    db.delete(e); db.commit(); return True


# ── Dashboard ─────────────────────────────────────────────────────────────────
def get_dashboard_stats(db: DBSession, user_id: int):
    today = date.today()
    hw_pending  = db.query(models.Homework).filter_by(user_id=user_id, completed=False).count()
    hw_overdue  = db.query(models.Homework).filter(
        models.Homework.user_id==user_id, models.Homework.completed==False,
        models.Homework.due_date < today).count()
    exams_upcoming = db.query(models.Exam).filter(
        models.Exam.user_id==user_id, models.Exam.completed==False,
        models.Exam.date >= today).count()
    all_grades = db.query(models.Grade).filter_by(user_id=user_id).all()
    total_weight = sum(g.weight for g in all_grades)
    overall_avg = sum(g.score * g.weight for g in all_grades) / total_weight if total_weight else 0
    return schemas.DashboardStats(
        homework_pending=hw_pending, homework_overdue=hw_overdue,
        exams_upcoming=exams_upcoming, overall_average=round(overall_avg, 2),
        total_grades=len(all_grades)
    )
