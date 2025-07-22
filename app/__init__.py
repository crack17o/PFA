from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_session import Session as FlaskSession
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
mail = Mail()
session_ext = FlaskSession()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    # Configure Flask-Session pour SQLAlchemy
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = db
    db.init_app(app)
    mail.init_app(app)
    session_ext.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)
    from app.controllers.api_faculty_controller import api_faculty_bp
    from app.controllers.api_role_controller import api_role_bp
    app.register_blueprint(api_faculty_bp)
    app.register_blueprint(api_role_bp)

    # Expiration de session après 1h d'inactivité
    from flask import session, redirect, url_for, request
    import datetime
    @app.before_request
    def check_session_expiry():
        session.permanent = True
        now = datetime.datetime.utcnow()
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity_dt = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            delta = (now - last_activity_dt).total_seconds()
            if delta > app.config.get('PERMANENT_SESSION_LIFETIME', 3600):
                session.clear()
                return redirect(url_for('auth.login'))
        session['last_activity'] = now.strftime('%Y-%m-%d %H:%M:%S')
    return app
