from flask import Blueprint, request, jsonify, session
from app.models.faculty import Promotion
from app.models.user import User
from app import db

promotion_bp = Blueprint('promotion', __name__)

@promotion_bp.route('/promotions', methods=['GET'])
def list_promotions():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    if user.role.name == 'faculty_admin':
        promotions = Promotion.query.filter_by(faculty_id=user.faculty_id).all()
    else:
        promotions = Promotion.query.all()
    return jsonify([
        {'id': p.id, 'name': p.name, 'faculty_id': p.faculty_id} for p in promotions
    ])
    
@promotion_bp.route('/promotions', methods=['POST'])
def create_promotion():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    name = data.get('name')
    faculty_id = data.get('faculty_id')
    # Restriction faculty admin
    if user.role.name == 'faculty_admin':
        faculty_id = user.faculty_id
    promotion = Promotion(name=name, faculty_id=faculty_id)
    db.session.add(promotion)
    db.session.commit()
    return jsonify({'message': 'Promotion created', 'id': promotion.id})

@promotion_bp.route('/promotions/<promotion_id>', methods=['PUT'])
def update_promotion(promotion_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    promotion = Promotion.query.get(promotion_id)
    if not user or not promotion or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    # Restriction faculty admin
    if user.role.name == 'faculty_admin' and promotion.faculty_id != user.faculty_id:
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json
    promotion.name = data.get('name', promotion.name)
    db.session.commit()
    return jsonify({'message': 'Promotion updated'})

@promotion_bp.route('/promotions/<promotion_id>', methods=['DELETE'])
def delete_promotion(promotion_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    promotion = Promotion.query.get(promotion_id)
    if not user or not promotion or user.role.name not in ['faculty_admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 401
    # Restriction faculty admin
    if user.role.name == 'faculty_admin' and promotion.faculty_id != user.faculty_id:
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(promotion)
    db.session.commit()
    return jsonify({'message': 'Promotion deleted'})
