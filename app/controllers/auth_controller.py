from flask import Blueprint, request, jsonify, session
from app.models.user import User, Role
from app import db, mail, limiter
from flask_mail import Message
import uuid, random
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit('5 per minute')
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role_name = data.get('role', 'student')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    promotion_id = data.get('promotion_id')
    department_id = data.get('department_id')
    faculty_id = data.get('faculty_id')
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({'error': 'Role not found'}), 400

    # Validation selon le rôle
    user_kwargs = {
        'email': email,
        'role_id': role.id,
        'first_name': first_name,
        'last_name': last_name
    }
    if role_name == 'student':
        if not promotion_id or not department_id:
            return jsonify({'error': 'Promotion et département requis pour les étudiants'}), 400
        user_kwargs['faculty_id'] = faculty_id
        user_kwargs['promotion_id'] = promotion_id
        user_kwargs['department_id'] = department_id
    elif role_name in ['prof', 'faculty_admin']:
        # Faculté requise
        if not faculty_id:
            return jsonify({'error': 'Faculté requise pour ce rôle'}), 400
        user_kwargs['faculty_id'] = faculty_id
    elif role_name == 'superadmin':
        # Rien d'obligatoire
        pass
    else:
        return jsonify({'error': 'Rôle inconnu'}), 400

    user = User(**user_kwargs)
    user.set_password(password)
    user.is_2fa_enabled = False  # Par défaut, 2FA désactivé
    db.session.add(user)
    db.session.commit()
    # Send welcome email (HTML stylisé)
    from flask import render_template
    from flask import current_app
    sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@unimate.com')
    msg = Message('Bienvenue sur UniMate', sender=sender, recipients=[email])
    msg.html = render_template('emails/welcome.html')
    mail.send(msg)
    return jsonify({'message': 'User registered successfully'})

@auth_bp.route('/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    # Détermine la redirection selon le rôle
    role_name = user.role.name if user.role else None
    if role_name == 'student':
        redirect_url = '/student/dashboard'
    elif role_name == 'prof':
        redirect_url = '/prof/dashboard'
    elif role_name == 'faculty_admin':
        redirect_url = '/faculty/dashboard'
    elif role_name == 'superadmin':
        redirect_url = '/admin/dashboard'
    else:
        redirect_url = '/'
    # OTP/2FA logic
    if user.is_2fa_enabled:
        from datetime import datetime, timedelta
        otp = str(random.randint(100000, 999999))
        session['otp'] = otp
        session['otp_expiry'] = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
        session['user_id'] = user.id
        session['role'] = user.role.name if user.role else None
        from flask import render_template, current_app
        sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@unimate.com')
        msg = Message('Votre code OTP', sender=sender, recipients=[email])
        msg.html = render_template('emails/otp.html', otp=otp)
        mail.send(msg)
        redirect_url = '/otp-login'
        return jsonify({'2fa_required': True, 'redirect_url': redirect_url})
    session['user_id'] = user.id
    session['role'] = user.role.name if user.role else None
    return jsonify({'message': 'Login successful', 'redirect_url': redirect_url})

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    from datetime import datetime
    otp = data.get('otp')
    otp_expiry = session.get('otp_expiry')
    if not otp_expiry or datetime.utcnow().timestamp() > otp_expiry:
        session.pop('otp', None)
        session.pop('otp_expiry', None)
        return jsonify({'error': 'OTP expired'}), 401
    if session.get('otp') == otp:
        session.pop('otp')
        session.pop('otp_expiry')
        # Récupère l'utilisateur connecté
        user_id = session.get('user_id')
        user = User.query.get(user_id) if user_id else None
        if user and user.role:
            role_name = user.role.name
            if role_name == 'student':
                redirect_url = '/student/dashboard'
            elif role_name == 'prof':
                redirect_url = '/prof/dashboard'
            elif role_name == 'faculty_admin':
                redirect_url = '/faculty/dashboard'
            elif role_name == 'superadmin':
                redirect_url = '/admin/dashboard'
            else:
                redirect_url = '/'
        else:
            redirect_url = '/'
        return jsonify({'message': 'OTP verified', 'redirect_url': redirect_url})
    return jsonify({'error': 'Invalid OTP'}), 401

@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit('5 per minute')
def reset_password():
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    from datetime import datetime, timedelta
    otp = str(random.randint(100000, 999999))
    session['reset_otp'] = otp
    session['reset_otp_expiry'] = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
    session['reset_user_id'] = user.id
    from flask import render_template, current_app
    sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@unimate.com')
    msg = Message('Réinitialisation du mot de passe', sender=sender, recipients=[email])
    msg.html = render_template('emails/reset_password.html', otp=otp)
    mail.send(msg)
    return jsonify({'message': 'OTP sent'})

@auth_bp.route('/confirm-reset', methods=['POST'])
def confirm_reset():
    data = request.json
    from datetime import datetime
    otp = data.get('otp')
    new_password = data.get('new_password')
    otp_expiry = session.get('reset_otp_expiry')
    if not otp_expiry or datetime.utcnow().timestamp() > otp_expiry:
        session.pop('reset_otp', None)
        session.pop('reset_otp_expiry', None)
        session.pop('reset_user_id', None)
        return jsonify({'error': 'OTP expired'}), 401
    if session.get('reset_otp') == otp:
        user = User.query.get(session.get('reset_user_id'))
        user.set_password(new_password)
        db.session.commit()
        session.pop('reset_otp')
        session.pop('reset_otp_expiry')
        session.pop('reset_user_id')
        return jsonify({'message': 'Password reset successful'})
    return jsonify({'error': 'Invalid OTP'}), 401
