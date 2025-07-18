import uuid
from app import db

class Faculty(db.Model):
    __tablename__ = 'faculties'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), unique=True, nullable=False)
    departments = db.relationship('Department', backref='faculty', lazy=True)
    promotions = db.relationship('Promotion', backref='faculty', lazy=True)
    users = db.relationship('User', backref='faculty', lazy=True)
    books = db.relationship('Book', backref='faculty', lazy=True)
    courses = db.relationship('Course', backref='faculty', lazy=True)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), nullable=False)
    faculty_id = db.Column(db.String(36), db.ForeignKey('faculties.id'), nullable=False)
    courses = db.relationship('Course', backref='department', lazy=True)

class Promotion(db.Model):
    __tablename__ = 'promotions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), nullable=False)
    faculty_id = db.Column(db.String(36), db.ForeignKey('faculties.id'), nullable=False)
    courses = db.relationship('Course', backref='promotion', lazy=True)
