from flask import Blueprint, request, jsonify, session, render_template, current_app
import os
import uuid
from app.models.book import Book
from app.models.user import User
from app import db, mail, limiter
from flask_mail import Message

book_bp = Blueprint('book', __name__)

@book_bp.route('/books', methods=['GET'])
def list_books():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    # Faculté obligatoire pour filtrer
    if not user.faculty_id:
        books = Book.query.all()
    else:
        books = Book.query.filter_by(faculty_id=user.faculty_id).all()
    return jsonify([
        {
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'file_url': b.file_url,
            'faculty_id': b.faculty_id,
            'faculty_name': b.faculty.name if hasattr(b, 'faculty') and b.faculty else None
        } for b in books
    ])

@book_bp.route('/books', methods=['POST'])
@limiter.limit('5 per minute')
def add_book():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    # Superadmin peut ajouter un livre dans n'importe quelle faculté
    faculty_id = request.form.get('faculty_id') if user.role.name == 'superadmin' else user.faculty_id
    if not faculty_id:
        return jsonify({'error': 'Missing faculty_id'}), 400
    if 'file' not in request.files:
        return jsonify({'error': 'Missing file'}), 400
    file = request.files['file']
    title = request.form.get('title')
    author = request.form.get('author')
    if not title or not author or not file:
        return jsonify({'error': 'Missing fields'}), 400
    # Générer un nom unique
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(current_app.root_path, 'static', 'books', unique_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)
    file_url = f"/static/books/{unique_name}"
    book = Book(title=title, author=author, file_url=file_url, faculty_id=faculty_id, added_by_id=user.id)
    db.session.add(book)
    db.session.commit()
    # Notifier tous les étudiants du département
    from app.models.user import Role
    student_role = Role.query.filter_by(name='student').first()
    students = User.query.filter_by(role_id=student_role.id, faculty_id=faculty_id).all()
    sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@unimate.com')
    for student in students:
        msg = Message('Nouveau livre disponible', sender=sender, recipients=[student.email])
        msg.html = render_template('emails/book_added.html', book_title=title)
        mail.send(msg)
    return jsonify({'message': 'Book added', 'id': book.id, 'file_url': file_url})

@book_bp.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    if not user or not book:
        return jsonify({'error': 'Unauthorized'}), 401
    # Superadmin peut supprimer n'importe quel livre
    if user.role.name == 'superadmin':
        pass
    elif user.role.name == 'prof' and book.added_by_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403
    elif user.role.name == 'faculty_admin' and book.faculty_id != user.faculty_id:
        return jsonify({'error': 'Forbidden'}), 403
    # Supprimer le fichier physique
    file_path = os.path.join(current_app.root_path, book.file_url.lstrip('/'))
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})

@book_bp.route('/books/<book_id>', methods=['PUT'])
@limiter.limit('5 per minute')
def edit_book(book_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    if not user or not book:
        return jsonify({'error': 'Unauthorized'}), 401
    # Superadmin peut éditer n'importe quel livre
    if user.role.name == 'superadmin':
        pass
    elif user.role.name == 'prof' and book.added_by_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403
    elif user.role.name == 'faculty_admin' and book.faculty_id != user.faculty_id:
        return jsonify({'error': 'Forbidden'}), 403
    # Faculté modifiable seulement par superadmin
    if user.role.name == 'superadmin':
        faculty_id = request.form.get('faculty_id', book.faculty_id)
        book.faculty_id = faculty_id
    # Mettre à jour les champs
    title = request.form.get('title', book.title)
    author = request.form.get('author', book.author)
    book.title = title
    book.author = author
    # Gérer le remplacement du fichier PDF
    if 'file' in request.files and request.files['file']:
        file = request.files['file']
        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(current_app.root_path, 'static', 'books', unique_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)
        # Supprimer l'ancien fichier
        if book.file_url:
            old_path = os.path.join(current_app.root_path, book.file_url.lstrip('/'))
            if os.path.exists(old_path):
                os.remove(old_path)
        book.file_url = f"/static/books/{unique_name}"
    db.session.commit()
    return jsonify({'message': 'Book updated', 'id': book.id, 'file_url': book.file_url})