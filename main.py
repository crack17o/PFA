import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


from app import create_app, db
from app.routes import register_blueprints

# Crée l'application
app = create_app()
register_blueprints(app)

# Ajout ProxyFix pour Render/proxy cloud
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

if __name__ == '__main__':
    # Modification pour écouter sur 0.0.0.0 pour le déploiement sur Render
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
