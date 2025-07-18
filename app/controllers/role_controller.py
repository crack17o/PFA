from flask import Blueprint, request, jsonify, session
from app.models.user import Role, User
from app import db

role_bp = Blueprint('role', __name__)

@role_bp.route('/roles', methods=['POST'])
def create_role():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    name = data.get('name')
    role = Role(name=name)
    db.session.add(role)
    db.session.commit()
    return jsonify({'message': 'Role created', 'id': role.id})

@role_bp.route('/roles/<role_id>', methods=['PUT'])
def update_role(role_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    role = Role.query.get(role_id)
    if not user or not role or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    role.name = data.get('name', role.name)
    db.session.commit()
    return jsonify({'message': 'Role updated'})

@role_bp.route('/roles/<role_id>', methods=['DELETE'])
def delete_role(role_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    role = Role.query.get(role_id)
    if not user or not role or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    db.session.delete(role)
    db.session.commit()
    return jsonify({'message': 'Role deleted'})
