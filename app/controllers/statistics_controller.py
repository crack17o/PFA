from flask import Blueprint, request, jsonify, session
from app.models.user import User
from app import db
from app.models.course import Course, Session
from app.models.faculty import Faculty, Promotion
from app.models.book import Book

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/stats/faculty', methods=['GET'])
def faculty_stats():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'faculty_admin':
        return jsonify({'error': 'Unauthorized'}), 401
    # Statistiques facultaires
    faculty_id = user.faculty_id
    nb_users = User.query.filter_by(faculty_id=faculty_id).count()
    nb_courses = Course.query.filter_by(faculty_id=faculty_id).count()
    nb_books = Book.query.filter_by(faculty_id=faculty_id).count()
    nb_sessions = Session.query.join(Course).filter(Course.faculty_id == faculty_id).count()
    stats = {
        'nb_users': nb_users,
        'nb_courses': nb_courses,
        'nb_books': nb_books,
        'nb_sessions': nb_sessions
    }
    return jsonify({'faculty_stats': stats})

@statistics_bp.route('/stats/global', methods=['GET'])
def global_stats():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role.name != 'superadmin':
        return jsonify({'error': 'Unauthorized'}), 401
    # Statistiques globales
    nb_users = User.query.count()
    nb_courses = Course.query.count()
    nb_books = Book.query.count()
    nb_sessions = Session.query.count()
    nb_faculties = Faculty.query.count()
    nb_promotions = Promotion.query.count()
    stats = {
        'nb_users': nb_users,
        'nb_courses': nb_courses,
        'nb_books': nb_books,
        'nb_sessions': nb_sessions,
        'nb_faculties': nb_faculties,
        'nb_promotions': nb_promotions
    }
    return jsonify({'global_stats': stats})
