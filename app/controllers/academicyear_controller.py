# Lister tous les semestres (superadmin)
from flask import Blueprint, request, jsonify, session
from app.models.course import AcademicYear, Semester
from app.models.user import User
from app import db

academicyear_bp = Blueprint('academicyear', __name__)

# Années académiques
@academicyear_bp.route('/superadmin/academicyears', methods=['GET'])
def list_academicyears():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    years = AcademicYear.query.order_by(AcademicYear.year.desc()).all()
    return jsonify([
        {
            'id': y.id,
            'year': y.year,
            'semesters': [{'id': s.id, 'name': s.name} for s in y.semesters]
        } for y in years
    ])

@academicyear_bp.route('/superadmin/academicyears', methods=['POST'])
def create_academicyear():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    year = data.get('year')
    if not year:
        return jsonify({'error': 'Missing year'}), 400
    ay = AcademicYear(year=year)
    db.session.add(ay)
    db.session.commit()
    return jsonify({'message': 'Année académique créée', 'id': ay.id})

@academicyear_bp.route('/superadmin/academicyears/<year_id>', methods=['PUT'])
def update_academicyear(year_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    ay = AcademicYear.query.get(year_id)
    if not user or not ay or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    ay.year = data.get('year', ay.year)
    db.session.commit()
    return jsonify({'message': 'Année académique modifiée'})

@academicyear_bp.route('/superadmin/academicyears/<year_id>', methods=['DELETE'])
def delete_academicyear(year_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    ay = AcademicYear.query.get(year_id)
    if not user or not ay or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    db.session.delete(ay)
    db.session.commit()
    return jsonify({'message': 'Année académique supprimée'})

# Semestres
@academicyear_bp.route('/superadmin/semesters', methods=['POST'])
def create_semester():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    name = data.get('name')
    academic_year_id = data.get('academic_year_id')
    if not name or not academic_year_id:
        return jsonify({'error': 'Missing fields'}), 400
    semester = Semester(name=name, academic_year_id=academic_year_id)
    db.session.add(semester)
    db.session.commit()
    return jsonify({'message': 'Semestre créé', 'id': semester.id})

@academicyear_bp.route('/superadmin/semesters/<semester_id>', methods=['PUT'])
def update_semester(semester_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    semester = Semester.query.get(semester_id)
    if not user or not semester or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    semester.name = data.get('name', semester.name)
    db.session.commit()
    return jsonify({'message': 'Semestre modifié'})

@academicyear_bp.route('/superadmin/semesters/<semester_id>', methods=['DELETE'])
def delete_semester(semester_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    semester = Semester.query.get(semester_id)
    if not user or not semester or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    db.session.delete(semester)
    db.session.commit()
    return jsonify({'message': 'Semestre supprimé'})

@academicyear_bp.route('/superadmin/semesters', methods=['GET'])
def list_semesters():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    semesters = Semester.query.order_by(Semester.name.asc()).all()
    return jsonify([
        {'id': s.id, 'name': s.name, 'academic_year_id': s.academic_year_id} for s in semesters
    ])