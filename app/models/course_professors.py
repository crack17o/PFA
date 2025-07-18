from app import db

course_professors = db.Table('course_professors',
    db.Column('course_id', db.String(36), db.ForeignKey('courses.id'), primary_key=True),
    db.Column('professor_id', db.String(36), db.ForeignKey('users.id'), primary_key=True)
)
