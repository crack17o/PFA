from flask import Blueprint, request, jsonify, session, current_app
from app.models.user import User
from app.models.course import Course, Session
from app import db
from app.models.book import Book
from datetime import datetime
import os

prof_bp = Blueprint('prof', __name__)

@prof_bp.route('/prof/dashboard', methods=['GET'])
def prof_dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'prof':
        return jsonify({'error': 'Unauthorized'}), 401
    courses = user.courses
    nb_courses = len(courses)
    nb_documents = Book.query.filter_by(added_by_id=user.id, faculty_id=user.faculty_id).count()
    today_sessions = []
    now = datetime.now().date()
    for course in courses:
        for session_obj in course.sessions:
            if session_obj.date and session_obj.date.date() == now:
                today_sessions.append({
                    'course': course.name,
                    'date': str(session_obj.date),
                    'status': session_obj.status,
                    'session_id': session_obj.id
                })
    stats = {
        'nb_courses': nb_courses,
        'nb_documents': nb_documents
    }
    return jsonify({'stats': stats, 'today_sessions': today_sessions})

@prof_bp.route('/prof/change-session-status', methods=['POST'])
def change_session_status():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'prof':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    session_id = data.get('session_id')
    status = data.get('status')
    session_obj = Session.query.get(session_id)
    if not session_obj:
        return jsonify({'error': 'Session not found'}), 404
    if session_obj.course not in user.courses:
        return jsonify({'error': 'Forbidden'}), 403
    session_obj.status = status
    db.session.commit()
    return jsonify({'message': 'Status updated', 'status': session_obj.status})

@prof_bp.route('/prof/courses', methods=['GET'])
def list_courses():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'prof':
        return jsonify({'error': 'Unauthorized'}), 401
    courses = user.courses
    return jsonify([{'id': c.id, 'name': c.name, 'credits': c.credits} for c in courses])

@prof_bp.route('/prof/courses/<course_id>/documents', methods=['GET'])
def list_documents(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    if not user or user.role.name != 'prof' or course not in user.courses:
        return jsonify({'error': 'Unauthorized'}), 401
    documents = Book.query.filter_by(added_by_id=user.id, faculty_id=user.faculty_id, course_id=course.id).all()
    return jsonify([{'id': d.id, 'title': d.title, 'file_path': d.file_url} for d in documents])

@prof_bp.route('/prof/courses/<course_id>/documents', methods=['POST'])
def add_document(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    if not user or user.role.name != 'prof' or course not in user.courses:
        return jsonify({'error': 'Unauthorized'}), 401
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    title = request.form.get('title')
    if not file or not title:
        return jsonify({'error': 'Missing fields'}), 400
    filename = f"{user.id}_{course.id}_{file.filename}"
    filepath = current_app.root_path + '/static/documents/' + filename
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    book = Book(title=title, author=user.email, file_url=f'/static/documents/{filename}', faculty_id=user.faculty_id, added_by_id=user.id, course_id=course.id)
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Document uploaded', 'id': book.id})

@prof_bp.route('/prof/courses/<course_id>/documents/<doc_id>', methods=['PUT'])
def update_document(course_id, doc_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    document = Book.query.get(doc_id)
    if not user or user.role.name != 'prof' or course not in user.courses or not document or document.added_by_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 401
    title = request.form.get('title')
    file = request.files.get('file')
    if title:
        document.title = title
    if file:
        filename = f"{user.id}_{course.id}_{file.filename}"
        filepath = current_app.root_path + '/static/documents/' + filename
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        old_path = current_app.root_path + document.file_url if document.file_url else None
        if old_path and os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass
        document.file_url = f'/static/documents/{filename}'
    db.session.commit()
    return jsonify({'message': 'Document updated', 'id': document.id})

@prof_bp.route('/prof/courses/<course_id>/documents/<doc_id>', methods=['DELETE'])
def delete_document(course_id, doc_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    document = Book.query.get(doc_id)
    if not user or user.role.name != 'prof' or course not in user.courses or not document or document.added_by_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 401
    file_path = current_app.root_path + document.file_url if document.file_url else None
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
    db.session.delete(document)
    db.session.commit()
    return jsonify({'message': 'Document deleted'})

# Export pour compatibilité
professor_bp = prof_bp