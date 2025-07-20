from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
import openai

views_bp = Blueprint('views', __name__)

# Pages principales
@views_bp.route('/')
def index():
    return render_template('index.html')

@views_bp.route('/about')
def about():
    return render_template('about.html')

# Authentification
@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@views_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@views_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    return render_template('reset_password.html')

# OTP
@views_bp.route('/otp-login', methods=['GET'])
def otp_login():
    return render_template('otp_login.html')

@views_bp.route('/otp-reset', methods=['GET'])
def otp_reset():
    return render_template('otp_reset.html')

# Interfaces étudiant
@views_bp.route('/student/dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@views_bp.route('/student/courses')
def student_courses():
    return render_template('student_courses.html')

@views_bp.route('/student/books')
def student_books():
    return render_template('student_books.html')

@views_bp.route('/student/profile')
def student_profile():
    return render_template('student_profile.html')

@views_bp.route('/student/chat-history')
def student_chat_history():
    return render_template('student_chat_history.html')

@views_bp.route('/student/notifications')
def student_notifications():
    return render_template('student_notifications.html')

# Interfaces professeur
@views_bp.route('/prof/dashboard')
def prof_dashboard():
    return render_template('prof_dashboard.html')

@views_bp.route('/prof/courses')
def prof_courses():
    return render_template('prof_courses.html')

@views_bp.route('/prof/documents')
def prof_documents():
    return render_template('prof_documents.html')

# Page de gestion des documents pour un cours spécifique (prof)
@views_bp.route('/prof/courses/<course_id>/documents')
def prof_course_documents(course_id):
    return render_template('prof_documents.html', course_id=course_id)

@views_bp.route('/prof/profile')
def prof_profile():
    return render_template('prof_profile.html')

@views_bp.route('/prof/chat-history')
def prof_chat_history():
    return render_template('prof_chat_history.html')

@views_bp.route('/prof/notifications')
def prof_notifications():
    return render_template('prof_notifications.html')

# Interfaces faculty
@views_bp.route('/faculty/dashboard')
def faculty_dashboard():
    return render_template('admin_dashboard.html')

@views_bp.route('/faculty/courses')
def faculty_courses():
    return render_template('admin_courses.html')

@views_bp.route('/faculty/books')
def faculty_books():
    return render_template('admin_books.html')

@views_bp.route('/faculty/profile')
def faculty_profile():
    return render_template('admin_profile.html')

@views_bp.route('/faculty/department')
def faculty_department():
    return render_template('admin_departments.html')

@views_bp.route('/faculty/promotion')
def faculty_promotion():
    return render_template('admin_promotions.html')

@views_bp.route('/faculty/users')
def faculty_users():
    return render_template('admin_users.html')

@views_bp.route('/student/chatbot')
def student_chatbot():
    return render_template('student_chatbot.html')

# Interfaces superadmin
@views_bp.route('/admin/dashboard')
def superadmin_dashboard():
    return render_template('superadmin_dashboard.html')

@views_bp.route('/admin/users')
def superadmin_users():
    return render_template('superadmin_users.html')

@views_bp.route('/admin/faculties')
def superadmin_faculties():
    return render_template('superadmin_faculties.html')

@views_bp.route('/admin/promotions')
def superadmin_promotions():
    return render_template('superadmin_promotions.html')

@views_bp.route('/admin/departments')
def superadmin_departments():
    return render_template('superadmin_departments.html')

@views_bp.route('/admin/courses')
def superadmin_courses():
    return render_template('superadmin_courses.html')

@views_bp.route('/admin/books')
def superadmin_books():
    return render_template('superadmin_books.html')

@views_bp.route('/admin/academicyears')
def superadmin_academicyears():
    return render_template('superadmin_academicyears.html')

@views_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.index'))

@views_bp.route('/chat/start', methods=['POST'])
def chat_start():
    from app.models.conversation import Conversation
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    conv = Conversation(user_id=user_id)
    from app import db
    db.session.add(conv)
    db.session.commit()
    return jsonify({'conversation_id': conv.id})

@views_bp.route('/chat/send', methods=['POST'])
def chat_send():
    from app.models.conversation import Conversation, Message
    data = request.json
    user_id = session.get('user_id')
    conv_id = data.get('conversation_id')
    content = data.get('content')
    if not user_id or not conv_id or not content:
        return jsonify({'error': 'Missing data'}), 400
    conv = Conversation.query.get(conv_id)
    if not conv or conv.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    msg = Message(conversation_id=conv_id, sender='user', content=content)
    from app import db
    db.session.add(msg)
    db.session.commit()
    # Récupérer l'historique
    history = [{'role': m.sender, 'content': m.content} for m in conv.messages]
    openai.api_key = 'YOUR_OPENAI_API_KEY'  # à remplacer par variable d'env
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=history
    )
    bot_content = response.choices[0].message['content']
    bot_msg = Message(conversation_id=conv_id, sender='bot', content=bot_content)
    db.session.add(bot_msg)
    db.session.commit()
    return jsonify({'bot_reply': bot_content})

