

# Auth & User
from app.controllers.auth_controller import auth_bp
from app.controllers.user_controller import user_bp

# Chatbot
from app.controllers.chatbot_controller import chatbot_bp

# Academic modules
from app.controllers.faculty_controller import faculty_bp
from app.controllers.department_controller import department_bp
from app.controllers.promotion_controller import promotion_bp
from app.controllers.course_controller import course_bp
from app.controllers.session_controller import session_bp
from app.controllers.book_controller import book_bp

# Admin & Roles
from app.controllers.admin_controller import admin_bp
from app.controllers.role_controller import role_bp

# Student & Professor
from app.controllers.student_controller import student_bp
from app.controllers.professor_controller import prof_bp

# Statistics & Export
from app.controllers.statistics_controller import statistics_bp
from app.controllers.export_controller import export_bp

def register_blueprints(app):
    # Auth & User
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')

    # Chatbot
    app.register_blueprint(chatbot_bp, url_prefix='/api')

    # Academic modules
    app.register_blueprint(faculty_bp, url_prefix='/api')
    app.register_blueprint(department_bp, url_prefix='/api')
    app.register_blueprint(promotion_bp, url_prefix='/api')
    app.register_blueprint(course_bp, url_prefix='/api')
    app.register_blueprint(session_bp, url_prefix='/api')
    app.register_blueprint(book_bp, url_prefix='/api')

    # Admin & Roles
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(role_bp, url_prefix='/api')

    # Student & Professor
    app.register_blueprint(student_bp, url_prefix='/api')
    app.register_blueprint(prof_bp, url_prefix='/api')

    # Statistics & Export
    app.register_blueprint(statistics_bp, url_prefix='/api')
    app.register_blueprint(export_bp, url_prefix='/api')

    # Academic Year & Semester (Superadmin)
    from app.controllers.academicyear_controller import academicyear_bp
    app.register_blueprint(academicyear_bp, url_prefix='/api')

    # Frontend views
    from app.views import views_bp
    app.register_blueprint(views_bp)
