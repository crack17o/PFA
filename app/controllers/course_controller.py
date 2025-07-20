from sqlalchemy import or_
from flask import Blueprint, request, jsonify, session
from app.models.course import Course, Session
from app.models.user import User
from app import db

course_bp = Blueprint('course', __name__)

@course_bp.route('/courses', methods=['GET'])
def list_courses():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    # Étudiant : ses cours, Prof : ses cours, Admin : tous les cours de la faculté
    if user.role.name == 'student':
        courses = user.courses
    elif user.role.name == 'prof':
        courses = user.courses
    elif user.role.name == 'faculty_admin':
        courses = Course.query.filter_by(faculty_id=user.faculty_id).all()
    else:
        courses = Course.query.all()
    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'credits': c.credits,
            'professors': [
                {
                    'id': p.id,
                    'name': f"{getattr(p, 'first_name', '')} {getattr(p, 'last_name', '')}".strip() if getattr(p, 'first_name', None) else p.email
                } for p in c.professors
            ]
        } for c in courses
    ])

@course_bp.route('/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'id': course.id, 'name': course.name, 'credits': course.credits})

@course_bp.route('/courses/<course_id>/sessions', methods=['GET'])
def get_sessions(course_id):
    sessions = Session.query.filter_by(course_id=course_id).all()
    return jsonify([{'id': s.id, 'date': s.date, 'status': s.status} for s in sessions])

@course_bp.route('/courses/<course_id>/sessions', methods=['POST'])
def add_session(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    if not user or not course:
        return jsonify({'error': 'Unauthorized'}), 401
    if user.role.name == 'faculty_admin':
        if course.faculty_id != user.faculty_id:
            return jsonify({'error': 'Unauthorized: faculty admin can only act on their own faculty'}), 403
    if user.role.name not in ['prof', 'faculty_admin']:
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json
    date = data.get('date')
    status = data.get('status', 'en attente')
    session_obj = Session(date=date, status=status, course_id=course_id)
    db.session.add(session_obj)
    db.session.commit()
    return jsonify({'message': 'Session added', 'id': session_obj.id})

@course_bp.route('/courses', methods=['POST'])
def create_course():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    # Seuls superadmin et faculty_admin peuvent créer un cours
    if user.role.name not in ['superadmin', 'faculty_admin']:
        return jsonify({'error': 'Forbidden'}), 403
    faculty_id = data.get('faculty_id')
    if user.role.name == 'faculty_admin' and faculty_id != user.faculty_id:
        return jsonify({'error': 'Unauthorized: faculty admin can only create in their own faculty'}), 403
    course = Course(
        name=data.get('name'),
        credits=data.get('credits'),
        department_id=data.get('department_id'),
        faculty_id=faculty_id,
        promotion_id=data.get('promotion_id'),
        semester_id=data.get('semester_id')
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({'message': 'Course created', 'id': course.id})

@course_bp.route('/courses/<course_id>', methods=['PUT'])
def update_course(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    if not user or not course:
        return jsonify({'error': 'Unauthorized'}), 401
    # Seuls superadmin et faculty_admin peuvent modifier un cours
    if user.role.name not in ['superadmin', 'faculty_admin']:
        return jsonify({'error': 'Forbidden'}), 403
    if user.role.name == 'faculty_admin' and course.faculty_id != user.faculty_id:
        return jsonify({'error': 'Unauthorized: faculty admin can only edit their own faculty'}), 403
    data = request.json
    course.name = data.get('name', course.name)
    course.credits = data.get('credits', course.credits)
    course.department_id = data.get('department_id', course.department_id)
    course.faculty_id = data.get('faculty_id', course.faculty_id)
    course.promotion_id = data.get('promotion_id', course.promotion_id)
    course.semester_id = data.get('semester_id', course.semester_id)
    db.session.commit()
    return jsonify({'message': 'Course updated'})

@course_bp.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    if not user or not course:
        return jsonify({'error': 'Unauthorized'}), 401
    # Seuls superadmin et faculty_admin peuvent supprimer un cours
    if user.role.name not in ['superadmin', 'faculty_admin']:
        return jsonify({'error': 'Forbidden'}), 403
    if user.role.name == 'faculty_admin' and course.faculty_id != user.faculty_id:
        return jsonify({'error': 'Unauthorized: faculty admin can only delete their own faculty'}), 403
    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': 'Course deleted'})

# CRUD pour les sessions
@course_bp.route('/courses/<course_id>/sessions/<session_id>', methods=['GET'])
def get_session(course_id, session_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    sess = Session.query.get(session_id)
    course = Course.query.get(course_id)
    if not user or not sess or not course or sess.course_id != course.id:
        return jsonify({'error': 'Unauthorized'}), 401
    # Professeur : doit être assigné au cours
    if user.role.name == 'prof' and user not in course.professors:
        return jsonify({'error': 'Forbidden'}), 403
    # Faculty admin : doit être sur sa faculté
    if user.role.name == 'faculty_admin' and course.faculty_id != user.faculty_id:
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify({'id': sess.id, 'date': sess.date, 'status': sess.status})

@course_bp.route('/courses/<course_id>/sessions/<session_id>', methods=['PUT'])
def update_session(course_id, session_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    sess = Session.query.get(session_id)
    course = Course.query.get(course_id)
    if not user or not sess or not course or sess.course_id != course.id:
        return jsonify({'error': 'Unauthorized'}), 401
    # Professeur : doit être assigné au cours
    if user.role.name == 'prof' and user not in course.professors:
        return jsonify({'error': 'Forbidden'}), 403
    # Faculty admin : doit être sur sa faculté
    if user.role.name == 'faculty_admin' and course.faculty_id != user.faculty_id:
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json
    sess.date = data.get('date', sess.date)
    sess.status = data.get('status', sess.status)
    db.session.commit()
    return jsonify({'message': 'Session updated'})

@course_bp.route('/courses/<course_id>/sessions/<session_id>', methods=['DELETE'])
def delete_session(course_id, session_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    sess = Session.query.get(session_id)
    course = Course.query.get(course_id)
    if not user or not sess or not course or sess.course_id != course.id:
        return jsonify({'error': 'Unauthorized'}), 401
    # Professeur : doit être assigné au cours
    if user.role.name == 'prof' and user not in course.professors:
        return jsonify({'error': 'Forbidden'}), 403
    # Faculty admin : doit être sur sa faculté
    if user.role.name == 'faculty_admin' and course.faculty_id != user.faculty_id:
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(sess)
    db.session.commit()
    return jsonify({'message': 'Session deleted'})
    