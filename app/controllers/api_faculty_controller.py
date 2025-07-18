from flask import Blueprint, jsonify
from app.models.faculty import Faculty, Department, Promotion

api_faculty_bp = Blueprint('api_faculty', __name__)

@api_faculty_bp.route('/api/faculties', methods=['GET'])
def get_faculties():
    faculties = Faculty.query.all()
    return jsonify([{'id': f.id, 'name': f.name} for f in faculties])

@api_faculty_bp.route('/api/faculties/<faculty_id>/departments', methods=['GET'])
def get_departments(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return jsonify([{'id': d.id, 'name': d.name} for d in departments])

@api_faculty_bp.route('/api/faculties/<faculty_id>/promotions', methods=['GET'])
def get_promotions(faculty_id):
    promotions = Promotion.query.filter_by(faculty_id=faculty_id).all()
    return jsonify([{'id': p.id, 'name': p.name} for p in promotions])
