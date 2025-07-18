import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.mysql import VARCHAR
from app import db

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(32), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'), nullable=False)
    faculty_id = db.Column(db.String(36), db.ForeignKey('faculties.id'), nullable=True)
    promotion_id = db.Column(db.String(36), db.ForeignKey('promotions.id'), nullable=True)
    department_id = db.Column(db.String(36), db.ForeignKey('departments.id'), nullable=True)
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(16))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    conversations = db.relationship('Conversation', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
