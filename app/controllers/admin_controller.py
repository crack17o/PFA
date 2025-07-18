from flask import Blueprint, request, jsonify, session
from app.models.user import User, Role
from app.models.course import Course
from app import db, mail, limiter
from flask_mail import Message

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/courses', methods=['GET'])
def list_courses_admin():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    if user.role.name == 'faculty_admin':
        courses = Course.query.filter_by(faculty_id=user.faculty_id).all()
    else:
        courses = Course.query.all()
    from app.models.course import course_professors
    result = []
    for c in courses:
        profs = db.session.query(User).join(course_professors, User.id == course_professors.c.professor_id)
        profs = profs.filter(course_professors.c.course_id == c.id).all()
        result.append({
            'id': c.id,
            'name': c.name,
            'credits': c.credits,
            'faculty_id': c.faculty_id,
            'faculty_name': c.faculty.name if hasattr(c, 'faculty') and c.faculty else None,
            'department_id': c.department_id,
            'department_name': c.department.name if hasattr(c, 'department') and c.department else None,
            'professors': [{'id': p.id, 'name': getattr(p, 'name', p.email)} for p in profs]
        })
    return jsonify(result)

@admin_bp.route('/admin/users', methods=['GET'])
def list_users():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    # Faculté admin : utilisateurs de sa faculté, superadmin : tous
    if user.role.name == 'faculty_admin':
        # Exclure faculty_admin et superadmin
        users = User.query.filter(
            User.faculty_id == user.faculty_id,
            ~User.role.has(Role.name.in_(['faculty_admin', 'superadmin']))
        ).all()
    else:
        users = User.query.all()
    return jsonify([
        {
            'id': u.id,
            'email': u.email,
            'role': u.role.name,
            'name': f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}".strip(),
            'faculty': {
                'id': u.faculty_id,
                'name': u.faculty.name if u.faculty else None
            },
            'promotion': {
                'id': u.promotion_id,
                'name': u.promotion.name if hasattr(u, 'promotion') and u.promotion else None
            },
            'department': {
                'id': u.department_id,
                'name': u.department.name if hasattr(u, 'department') and u.department else None
            }
        } for u in users
    ])

@admin_bp.route('/admin/courses/<course_id>/assign', methods=['POST'])
@limiter.limit('5 per minute')
def assign_course(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    prof_id = data.get('professor_id')
    prof = User.query.get(prof_id)
    course = Course.query.get(course_id)
    if not prof or not course:
        return jsonify({'error': 'Not found'}), 404
    # Restriction faculty admin
    if user.role.name == 'faculty_admin':
        if course.faculty_id != user.faculty_id or prof.faculty_id != user.faculty_id:
            return jsonify({'error': 'Unauthorized: faculty admin can only act on their own faculty'}), 403
    course.professors.append(prof)
    db.session.commit()
    # Envoi email stylisé
    from flask import render_template
    from flask import current_app
    sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@unimate.com')
    msg = Message('Affectation de cours', sender=sender, recipients=[prof.email])
    msg.html = render_template('emails/course_assigned.html', course_name=course.name)
    mail.send(msg)
    return jsonify({'message': 'Course assigned'})

@admin_bp.route('/admin/courses/<course_id>/unassign', methods=['POST'])
@limiter.limit('5 per minute')
def unassign_course(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    prof_id = data.get('professor_id')
    prof = User.query.get(prof_id)
    course = Course.query.get(course_id)
    if not prof or not course:
        return jsonify({'error': 'Not found'}), 404
    # Restriction faculty admin
    if user.role.name == 'faculty_admin':
        if course.faculty_id != user.faculty_id or prof.faculty_id != user.faculty_id:
            return jsonify({'error': 'Unauthorized: faculty admin can only act on their own faculty'}), 403
    if prof in course.professors:
        course.professors.remove(prof)
        db.session.commit()
        # Envoi email stylisé
        from flask import render_template
        from flask import current_app
        sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@unimate.com')
        msg = Message('Retrait de cours', sender=sender, recipients=[prof.email])
        msg.html = render_template('emails/course_unassigned.html', course_name=course.name)
        mail.send(msg)
    return jsonify({'message': 'Course unassigned'})

@admin_bp.route('/admin/courses', methods=['POST'])
@limiter.limit('5 per minute')
def create_course():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    name = data.get('name')
    credits = data.get('credits')
    department_id = data.get('department_id')
    promotion_id = data.get('promotion_id')
    faculty_id = data.get('faculty_id') or user.faculty_id
    semester_id = data.get('semester_id')
    if not all([name, credits, department_id, promotion_id, faculty_id, semester_id]):
        return jsonify({'error': 'Missing fields'}), 400
    # Restriction faculty admin
    if user.role.name == 'faculty_admin':
        faculty_id = user.faculty_id
    course = Course(name=name, credits=credits, department_id=department_id, promotion_id=promotion_id, faculty_id=faculty_id, semester_id=semester_id)
    db.session.add(course)
    db.session.commit()
    return jsonify({'message': 'Course created', 'id': course.id})

@admin_bp.route('/admin/courses/<course_id>', methods=['PUT', 'PATCH'])
@limiter.limit('5 per minute')
def edit_course(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Not found'}), 404
    # Restriction faculty admin
    if user.role.name == 'faculty_admin' and course.faculty_id != user.faculty_id:
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json
    course.name = data.get('name', course.name)
    course.credits = data.get('credits', course.credits)
    course.department_id = data.get('department_id', course.department_id)
    course.promotion_id = data.get('promotion_id', course.promotion_id)
    # Faculté non modifiable par faculty admin
    if user.role.name == 'faculty_admin':
        course.faculty_id = user.faculty_id
    else:
        course.faculty_id = data.get('faculty_id', course.faculty_id)
    course.semester_id = data.get('semester_id', course.semester_id)
    db.session.commit()
    return jsonify({'message': 'Course updated', 'id': course.id})

@admin_bp.route('/admin/courses/<course_id>', methods=['DELETE'])
@limiter.limit('5 per minute')
def delete_course(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Not found'}), 404
    # Restriction faculty admin
    if user.role.name == 'faculty_admin' and course.faculty_id != user.faculty_id:
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': 'Course deleted', 'id': course_id})