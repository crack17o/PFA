from flask import Blueprint, request, jsonify, session
from app.models.course import AcademicYear, Semester
from app.models.user import User
from app import db

academic_bp = Blueprint('academic', __name__)

@academic_bp.route('/academic_years', methods=['POST'])
def create_academic_year():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    year = data.get('year')
    ay = AcademicYear(year=year)
    db.session.add(ay)
    db.session.commit()
    return jsonify({'message': 'Academic year created', 'id': ay.id})

@academic_bp.route('/academic_years/<ay_id>', methods=['PUT'])
def update_academic_year(ay_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    ay = AcademicYear.query.get(ay_id)
    if not user or not ay or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    ay.year = data.get('year', ay.year)
    db.session.commit()
    return jsonify({'message': 'Academic year updated'})

@academic_bp.route('/academic_years/<ay_id>', methods=['DELETE'])
def delete_academic_year(ay_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    ay = AcademicYear.query.get(ay_id)
    if not user or not ay or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    db.session.delete(ay)
    db.session.commit()
    return jsonify({'message': 'Academic year deleted'})

@academic_bp.route('/semesters', methods=['POST'])
def create_semester():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    name = data.get('name')
    academic_year_id = data.get('academic_year_id')
    semester = Semester(name=name, academic_year_id=academic_year_id)
    db.session.add(semester)
    db.session.commit()
    return jsonify({'message': 'Semester created', 'id': semester.id})

@academic_bp.route('/semesters/<semester_id>', methods=['PUT'])
def update_semester(semester_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    semester = Semester.query.get(semester_id)
    if not user or not semester or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    semester.name = data.get('name', semester.name)
    db.session.commit()
    return jsonify({'message': 'Semester updated'})

@academic_bp.route('/semesters/<semester_id>', methods=['DELETE'])
def delete_semester(semester_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    semester = Semester.query.get(semester_id)
    if not user or not semester or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    db.session.delete(semester)
    db.session.commit()
    return jsonify({'message': 'Semester deleted'})
