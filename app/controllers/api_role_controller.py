from flask import Blueprint, jsonify
from app.models.user import Role

api_role_bp = Blueprint('api_role', __name__)

@api_role_bp.route('/api/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    return jsonify([{'id': r.id, 'name': r.name} for r in roles])
