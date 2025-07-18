from flask import Blueprint, request, jsonify, session
from app.models.user import User
from app import db

export_bp = Blueprint('export', __name__)

@export_bp.route('/export/full', methods=['GET'])
def full_export():
    import json
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    # Export all tables as JSON
    from app.models.user import User, Role
    from app.models.faculty import Faculty, Department, Promotion
    from app.models.course import Course, Semester, AcademicYear, Session
    from app.models.book import Book
    from app.models.conversation import Conversation, Message
    users = [u.__dict__.copy() for u in User.query.all()]
    for u in users:
        u.pop('_sa_instance_state', None)
    roles = [r.__dict__.copy() for r in Role.query.all()]
    for r in roles:
        r.pop('_sa_instance_state', None)
    faculties = [f.__dict__.copy() for f in Faculty.query.all()]
    for f in faculties:
        f.pop('_sa_instance_state', None)
    departments = [d.__dict__.copy() for d in Department.query.all()]
    for d in departments:
        d.pop('_sa_instance_state', None)
    promotions = [p.__dict__.copy() for p in Promotion.query.all()]
    for p in promotions:
        p.pop('_sa_instance_state', None)
    courses = [c.__dict__.copy() for c in Course.query.all()]
    for c in courses:
        c.pop('_sa_instance_state', None)
    semesters = [s.__dict__.copy() for s in Semester.query.all()]
    for s in semesters:
        s.pop('_sa_instance_state', None)
    academic_years = [a.__dict__.copy() for a in AcademicYear.query.all()]
    for a in academic_years:
        a.pop('_sa_instance_state', None)
    sessions = [s.__dict__.copy() for s in Session.query.all()]
    for s in sessions:
        s.pop('_sa_instance_state', None)
    books = [b.__dict__.copy() for b in Book.query.all()]
    for b in books:
        b.pop('_sa_instance_state', None)
    conversations = [c.__dict__.copy() for c in Conversation.query.all()]
    for c in conversations:
        c.pop('_sa_instance_state', None)
    messages = [m.__dict__.copy() for m in Message.query.all()]
    for m in messages:
        m.pop('_sa_instance_state', None)
    data = {
        'users': users,
        'roles': roles,
        'faculties': faculties,
        'departments': departments,
        'promotions': promotions,
        'courses': courses,
        'semesters': semesters,
        'academic_years': academic_years,
        'sessions': sessions,
        'books': books,
        'conversations': conversations,
        'messages': messages
    }
    return jsonify({'export': data})

@export_bp.route('/system/health', methods=['GET'])
def system_health():
    import socket
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    # Vérification base de données
    db_status = 'OK'
    try:
        db.session.execute('SELECT 1')
    except Exception:
        db_status = 'ERROR'
    # Vérification mail
    mail_status = 'OK'
    try:
        # Test simple de connexion SMTP
        import smtplib
        from flask import current_app
        server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'], timeout=5)
        server.quit()
    except Exception:
        mail_status = 'ERROR'
    # Vérification réseau
    network_status = 'OK'
    try:
        socket.gethostbyname('google.com')
    except Exception:
        network_status = 'ERROR'
    return jsonify({
        'status': 'OK' if db_status == 'OK' and mail_status == 'OK' and network_status == 'OK' else 'ERROR',
        'db': db_status,
        'mail': mail_status,
        'network': network_status
    })
