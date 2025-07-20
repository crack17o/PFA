from flask import Blueprint, request, jsonify, session
from app.models.user import User
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'email': user.email, 'role': user.role.name, 'is_2fa_enabled': user.is_2fa_enabled})


@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    updated = False
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    if email:
        user.email = email
        updated = True
    if first_name:
        user.first_name = first_name
        updated = True
    if last_name:
        user.last_name = last_name
        updated = True
    if updated:
        db.session.commit()
        return jsonify({'message': 'Profil mis à jour.'})
    return jsonify({'message': 'Aucune modification.'})

@user_bp.route('/profile/password', methods=['PUT'])
def change_password():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if not old_password or not new_password:
        return jsonify({'error': 'Missing password fields'}), 400
    if not user.check_password(old_password):
        return jsonify({'error': 'Incorrect old password'}), 401
    user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Password updated'})

@user_bp.route('/profile/2fa', methods=['POST'])
def toggle_2fa():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    enable = data.get('enable', False)
    user.is_2fa_enabled = enable
    db.session.commit()
    return jsonify({'message': '2FA updated', 'is_2fa_enabled': user.is_2fa_enabled})

@user_bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'id': user.id,
        'email': user.email,
        'role': user.role.name if user.role else None,
        'faculty_id': user.faculty_id,
        'first_name': user.first_name,
        'last_name': user.last_name
    })
