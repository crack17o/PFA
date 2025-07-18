from app import db

student_courses = db.Table('student_courses',
    db.Column('student_id', db.String(36), db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.String(36), db.ForeignKey('courses.id'), primary_key=True)
)
