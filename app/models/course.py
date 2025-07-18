import uuid
from app import db
from app.models.course_professors import course_professors

class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    year = db.Column(db.String(9), nullable=False)  # ex: 2024-2025
    semesters = db.relationship('Semester', backref='academic_year', lazy=True)

class Semester(db.Model):
    __tablename__ = 'semesters'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(32), nullable=False)
    academic_year_id = db.Column(db.String(36), db.ForeignKey('academic_years.id'), nullable=False)
    courses = db.relationship('Course', backref='semester', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.String(36), db.ForeignKey('departments.id'), nullable=False)
    promotion_id = db.Column(db.String(36), db.ForeignKey('promotions.id'), nullable=False)
    faculty_id = db.Column(db.String(36), db.ForeignKey('faculties.id'), nullable=False)
    semester_id = db.Column(db.String(36), db.ForeignKey('semesters.id'), nullable=False)
    sessions = db.relationship('Session', backref='course', lazy=True)
    professors = db.relationship('User', secondary='course_professors', backref='courses')

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(16), nullable=False)  # levée, annulée, en attente
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False)
