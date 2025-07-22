import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.routes import register_blueprints

# Crée l'application
app = create_app()
register_blueprints(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # Modification pour écouter sur 0.0.0.0 pour le déploiement sur Render
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
