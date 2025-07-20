from flask import Blueprint, request, jsonify, session, current_app
from app.models.user import User
from app.models.course import Course, Session
from app.models.user import Role
from app import db
from app.models.book import Book
from datetime import datetime
import os

from flask import render_template
from flask_mail import Message
def send_session_mail(recipients, subject, template, **kwargs):
    mail = current_app.extensions.get('mail')
    if not mail:
        return
    msg = Message(subject, recipients=recipients)
    msg.html = render_template(template, **kwargs)
    try:
        mail.send(msg)
    except Exception:
        pass
    
prof_bp = Blueprint('prof', __name__)

@prof_bp.route('/prof/sessions', methods=['POST'])
def add_prof_session():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'prof':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    course_id = data.get('course_id')
    date = data.get('date')
    status = data.get('status', 'en attente')
    course = Course.query.get(course_id)
    if not course or course not in user.courses:
        return jsonify({'error': 'Forbidden'}), 403
    # Vérification date/heure passée
    try:
        session_dt = datetime.fromisoformat(date)
    except Exception:
        return jsonify({'error': 'Date invalide'}), 400
    if session_dt < datetime.now():
        return jsonify({'error': 'Impossible de créer une séance à une date/heure passée.'}), 400
    session_obj = Session(date=session_dt, status=status, course_id=course_id)
    db.session.add(session_obj)
    db.session.commit()
    # Notifier si levée
    if status == 'levée':
        promotion = course.promotion
        if promotion:
            student_role = Role.query.filter_by(name='student').first()
            students = [u for u in promotion.users if u.role_id == student_role.id]
            sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@unimate.com')
            mail = current_app.extensions.get('mail')
            for student in students:
                msg = Message('Séance levée', sender=sender, recipients=[student.email])
                msg.html = render_template('emails/session_raised.html', course_name=course.name, session_date=session_dt)
                try:
                    mail.send(msg)
                except Exception:
                    pass
    return jsonify({'message': 'Session créée', 'id': session_obj.id})

@prof_bp.route('/prof/sessions/<session_id>', methods=['PUT'])
def edit_prof_session(session_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    session_obj = Session.query.get(session_id)
    if not user or user.role.name != 'prof' or not session_obj or session_obj.course not in user.courses:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    old_status = session_obj.status
    # Vérification date/heure passée
    new_date = data.get('date', session_obj.date)
    try:
        session_dt = datetime.fromisoformat(new_date) if isinstance(new_date, str) else new_date
    except Exception:
        return jsonify({'error': 'Date invalide'}), 400
    if session_dt < datetime.now():
        return jsonify({'error': 'Impossible de modifier une séance à une date/heure passée.'}), 400
    session_obj.date = session_dt
    session_obj.status = data.get('status', session_obj.status)
    db.session.commit()
    course = session_obj.course
    promotion = course.promotion
    # Mail si passage à levée
    if old_status != 'levée' and session_obj.status == 'levée':
        if promotion:
            student_role = Role.query.filter_by(name='student').first()
            students = [u for u in promotion.users if u.role_id == student_role.id]
            sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@unimate.com')
            mail = current_app.extensions.get('mail')
            for student in students:
                msg = Message('Séance levée', sender=sender, recipients=[student.email])
                msg.html = render_template('emails/session_raised.html', course_name=course.name, session_date=session_obj.date)
                try:
                    mail.send(msg)
                except Exception:
                    pass
    # Mail si passage de levée à confirmée
    if old_status == 'levée' and session_obj.status == 'confirmée':
        if promotion:
            student_role = Role.query.filter_by(name='student').first()
            students = [u for u in promotion.users if u.role_id == student_role.id]
            sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@unimate.com')
            mail = current_app.extensions.get('mail')
            for student in students:
                msg = Message('Séance confirmée', sender=sender, recipients=[student.email])
                msg.html = render_template('emails/session_confirmed.html', course_name=course.name, session_date=session_obj.date)
                try:
                    mail.send(msg)
                except Exception:
                    pass
    return jsonify({'message': 'Session modifiée'})

@prof_bp.route('/prof/sessions/<session_id>', methods=['DELETE'])
def delete_prof_session(session_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    session_obj = Session.query.get(session_id)
    if not user or user.role.name != 'prof' or not session_obj or session_obj.course not in user.courses:
        return jsonify({'error': 'Unauthorized'}), 401
    db.session.delete(session_obj)
    db.session.commit()
    return jsonify({'message': 'Session supprimée'})

@prof_bp.route('/prof/sessions', methods=['GET'])
def list_prof_sessions():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'prof':
        return jsonify({'error': 'Unauthorized'}), 401
    sessions = []
    for course in user.courses:
        for s in course.sessions:
            sessions.append({
                'id': s.id,
                'date': s.date.isoformat() if s.date else None,
                'status': s.status,
                'course_id': course.id,
                'course_name': course.name
            })
    return jsonify(sessions)

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
    result = []
    for c in courses:
        result.append({
            'id': c.id,
            'name': c.name,
            'credits': c.credits,
            'department_name': c.department.name if c.department else None,
            'promotion_name': c.promotion.name if c.promotion else None,
            'semester_name': c.semester.name if c.semester else None
        })
    return jsonify(result)

@prof_bp.route('/prof/documents', methods=['GET'])
def list_documents():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'prof':
        return jsonify({'error': 'Unauthorized'}), 401
    documents = Book.query.filter_by(added_by_id=user.id, faculty_id=user.faculty_id).all()
    return jsonify([{'id': d.id, 'title': d.title, 'file_path': d.file_url, 'author': d.author} for d in documents])

@prof_bp.route('/prof/documents', methods=['POST'])
def add_document():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'prof':
        return jsonify({'error': 'Unauthorized'}), 401
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    title = request.form.get('title')
    if not file or not title:
        return jsonify({'error': 'Missing fields'}), 400
    filename = f"{user.id}_{file.filename}"
    filepath = current_app.root_path + '/static/books/' + filename
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    book = Book(title=title, author=user.email, file_url=f'/static/books/{filename}', faculty_id=user.faculty_id, added_by_id=user.id)
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Document uploaded', 'id': book.id})

@prof_bp.route('/prof/documents/<doc_id>', methods=['PUT'])
def update_document(doc_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    document = Book.query.get(doc_id)
    if not user or user.role.name != 'prof' or not document or document.added_by_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 401
    title = request.form.get('title')
    file = request.files.get('file')
    if title:
        document.title = title
    if file:
        filename = f"{user.id}_{file.filename}"
        filepath = current_app.root_path + '/static/books/' + filename
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        old_path = current_app.root_path + document.file_url if document.file_url else None
        if old_path and os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass
        document.file_url = f'/static/books/{filename}'
    db.session.commit()
    return jsonify({'message': 'Document updated', 'id': document.id})

@prof_bp.route('/prof/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    document = Book.query.get(doc_id)
    if not user or user.role.name != 'prof' or not document or document.added_by_id != user.id:
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

@prof_bp.route('/prof/sessions/today', methods=['GET'])
def list_today_sessions():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'prof':
        return jsonify({'error': 'Unauthorized'}), 401
    today = datetime.now().date()
    today_sessions = []
    for course in user.courses:
        for session_obj in course.sessions:
            if session_obj.date and session_obj.date.date() == today:
                today_sessions.append({
                    'id': session_obj.id,
                    'date': session_obj.date.isoformat() if session_obj.date else None,
                    'status': session_obj.status,
                    'course_id': course.id,
                    'course_name': course.name
                })
    return jsonify(today_sessions)

# Export pour compatibilité
professor_bp = prof_bp