import uuid
from app import db

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(128), nullable=False)
    author = db.Column(db.String(64), nullable=False)
    file_url = db.Column(db.String(256), nullable=False)
    faculty_id = db.Column(db.String(36), db.ForeignKey('faculties.id'), nullable=False)
    added_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    added_by = db.relationship('User', backref='added_books')
