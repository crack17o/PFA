from flask import Blueprint, request, jsonify, session as flask_session
from app.models.course import Session
from app.models.user import User
from app import db

session_bp = Blueprint('session', __name__)

@session_bp.route('/sessions/<session_id>', methods=['PUT'])
def update_session(session_id):
    user_id = flask_session.get('user_id')
    user = User.query.get(user_id)
    session_obj = Session.query.get(session_id)
    if not user or not session_obj:
        return jsonify({'error': 'Unauthorized'}), 401
    if user.role.name == 'faculty_admin':
        if not session_obj.course or session_obj.course.faculty_id != user.faculty_id:
            return jsonify({'error': 'Unauthorized: faculty admin can only act on their own faculty'}), 403
    if user.role.name not in ['prof', 'faculty_admin']:
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json
    session_obj.date = data.get('date', session_obj.date)
    session_obj.status = data.get('status', session_obj.status)
    db.session.commit()
    return jsonify({'message': 'Session updated'})

@session_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    user_id = flask_session.get('user_id')
    user = User.query.get(user_id)
    session_obj = Session.query.get(session_id)
    if not user or not session_obj:
        return jsonify({'error': 'Unauthorized'}), 401
    if user.role.name == 'faculty_admin':
        if not session_obj.course or session_obj.course.faculty_id != user.faculty_id:
            return jsonify({'error': 'Unauthorized: faculty admin can only act on their own faculty'}), 403
    if user.role.name not in ['prof', 'faculty_admin']:
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(session_obj)
    db.session.commit()
    return jsonify({'message': 'Session deleted'})
