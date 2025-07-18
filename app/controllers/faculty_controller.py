from flask import Blueprint, request, jsonify, session
from app.models.faculty import Faculty, Department, Promotion
from app.models.user import User
from app import db

faculty_bp = Blueprint('faculty', __name__)

@faculty_bp.route('/faculties', methods=['GET'])
def list_faculties():
    faculties = Faculty.query.all()
    return jsonify([{'id': f.id, 'name': f.name} for f in faculties])

# CRUD operations for faculties (superadmin only)
def is_superadmin():
    user_id = session.get('user_id')
    if not user_id:
        return False
    user = User.query.get(user_id)
    return user and user.role and user.role.name == 'superadmin'

@faculty_bp.route('/faculties', methods=['POST'])
def create_faculty():
    if not is_superadmin():
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    faculty = Faculty(name=name)
    db.session.add(faculty)
    db.session.commit()
    return jsonify({'id': faculty.id, 'name': faculty.name}), 201

@faculty_bp.route('/faculties/<faculty_id>', methods=['PUT'])
def update_faculty(faculty_id):
    if not is_superadmin():
        return jsonify({'error': 'Unauthorized'}), 403
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({'error': 'Faculty not found'}), 404
    data = request.json
    name = data.get('name')
    if name:
        faculty.name = name
    db.session.commit()
    return jsonify({'id': faculty.id, 'name': faculty.name})

@faculty_bp.route('/faculties/<faculty_id>', methods=['DELETE'])
def delete_faculty(faculty_id):
    if not is_superadmin():
        return jsonify({'error': 'Unauthorized'}), 403
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({'error': 'Faculty not found'}), 404
    db.session.delete(faculty)
    db.session.commit()
    return jsonify({'message': 'Faculty deleted'})

@faculty_bp.route('/faculties/<faculty_id>/departments', methods=['GET'])
def list_departments(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return jsonify([{'id': d.id, 'name': d.name} for d in departments])

@faculty_bp.route('/faculties/<faculty_id>/promotions', methods=['GET'])
def list_promotions(faculty_id):
    promotions = Promotion.query.filter_by(faculty_id=faculty_id).all()
    return jsonify([{'id': p.id, 'name': p.name} for p in promotions])
