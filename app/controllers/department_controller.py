from flask import Blueprint, request, jsonify, session
from app.models.faculty import Department
from app.models.user import User
from app import db

department_bp = Blueprint('department', __name__)

@department_bp.route('/departments', methods=['POST'])
def create_department():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    name = data.get('name')
    faculty_id = data.get('faculty_id')
    # Restriction faculty admin
    if user.role.name == 'faculty_admin' and faculty_id != user.faculty_id:
        return jsonify({'error': 'Unauthorized: faculty admin can only act on their own faculty'}), 403
    department = Department(name=name, faculty_id=faculty_id)
    db.session.add(department)
    db.session.commit()
    return jsonify({'message': 'Department created', 'id': department.id})

@department_bp.route('/departments/<department_id>', methods=['PUT'])
def update_department(department_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    department = Department.query.get(department_id)
    if not user or not department or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    # Restriction faculty admin
    if user.role.name == 'faculty_admin' and department.faculty_id != user.faculty_id:
        return jsonify({'error': 'Unauthorized: faculty admin can only act on their own faculty'}), 403
    data = request.json
    department.name = data.get('name', department.name)
    db.session.commit()
    return jsonify({'message': 'Department updated'})

@department_bp.route('/departments/<department_id>', methods=['DELETE'])
def delete_department(department_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    department = Department.query.get(department_id)
    if not user or not department or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    # Restriction faculty admin
    if user.role.name == 'faculty_admin' and department.faculty_id != user.faculty_id:
        return jsonify({'error': 'Unauthorized: faculty admin can only act on their own faculty'}), 403
    db.session.delete(department)
    db.session.commit()
    return jsonify({'message': 'Department deleted'})

@department_bp.route('/departments', methods=['GET'])
def list_departments():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    # Faculté admin : départements de sa faculté, superadmin : tous
    if user.role.name == 'faculty_admin':
        departments = Department.query.filter_by(faculty_id=user.faculty_id).all()
    else:
        departments = Department.query.all()
    return jsonify([
        {
            'id': d.id,
            'name': d.name,
            'faculty_id': d.faculty_id,
            'faculty_name': d.faculty.name if d.faculty else None
        } for d in departments
    ])