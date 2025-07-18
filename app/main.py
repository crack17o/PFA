import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.routes import register_blueprints

app = create_app()
register_blueprints(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
