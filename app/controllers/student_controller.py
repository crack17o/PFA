from flask import Blueprint, request, jsonify, session
from app.models.user import User
from app.models.course import Course
from app.models.student_courses import student_courses
from app import db

student_bp = Blueprint('student', __name__)

@student_bp.route('/student/courses', methods=['POST'])
def enroll_course():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    course_id = data.get('course_id')
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    user.courses.append(course)
    db.session.commit()
    return jsonify({'message': 'Enrolled in course'})

@student_bp.route('/student/courses/<course_id>', methods=['DELETE'])
def unenroll_course(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    course = Course.query.get(course_id)
    if not course or course not in user.courses:
        return jsonify({'error': 'Course not found'}), 404
    user.courses.remove(course)
    db.session.commit()
    return jsonify({'message': 'Unenrolled from course'})

@student_bp.route('/student/dashboard', methods=['GET'])
def student_dashboard():
    from datetime import datetime
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    # Statistiques
    nb_courses = len(user.courses)
    # Livres (accessible à tous les étudiants connectés)
    from app.models.book import Book
    if hasattr(user, 'faculty_id') and user.faculty_id:
        books = Book.query.filter_by(faculty_id=user.faculty_id).limit(5).all()
        nb_books = Book.query.filter_by(faculty_id=user.faculty_id).count()
    else:
        books = Book.query.limit(3).all()
        nb_books = Book.query.count()
    # Séances du jour
    today = datetime.now().date()
    sessions_today = []
    for course in user.courses:
        for s in course.sessions:
            if s.date.date() == today:
                sessions_today.append({
                    'course_name': course.name,
                    'date': s.date.strftime('%H:%M'),
                    'status': s.status
                })
    # Détails des cours
    courses_list = [
        {'name': c.name, 'credits': c.credits} for c in user.courses
    ]
    # Livres récents
    books_list = [
        {'title': b.title, 'author': b.author, 'file_url': b.file_url} for b in books
    ]
    stats = {
        'nb_courses': nb_courses,
        'nb_books': nb_books,
        'courses': courses_list,
        'books': books_list
    }
    return jsonify({'stats': stats, 'sessions_today': sessions_today})

@student_bp.route('/student/courses', methods=['GET'])
def get_student_courses():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    courses = []
    for course in user.courses:
        sessions = [
            {'id': s.id, 'date': s.date.strftime('%Y-%m-%d %H:%M'), 'status': s.status}
            for s in course.sessions
        ]
        courses.append({
            'id': course.id,
            'name': course.name,
            'credits': course.credits,
            'sessions': sessions
        })
    return jsonify({'courses': courses})

@student_bp.route('/student/promotion/courses', methods=['GET'])
def get_promotion_courses():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'student' or not user.promotion_id:
        return jsonify({'error': 'Unauthorized'}), 401
    promotion = user.promotion
    if not promotion:
        return jsonify({'error': 'No promotion found'}), 404
    courses = promotion.courses
    result = []
    for c in courses:
        result.append({
            'id': c.id,
            'name': c.name,
            'credits': c.credits,
            'department_name': c.department.name if c.department else None,
            'faculty_name': c.faculty.name if c.faculty else None,
            'semester_name': c.semester.name if hasattr(c, 'semester') and c.semester else None
        })
    return jsonify({'courses': result})
