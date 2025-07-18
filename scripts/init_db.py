
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import db, create_app
from app.models.faculty import Faculty, Department, Promotion
from app.models.user import Role
ROLES = ['student', 'professor', 'admin', 'superadmin']

app = create_app()

FACULTIES = [
    {'name': 'Sciences'},
    {'name': 'Lettres'},
    {'name': 'Droit'},
    {'name': 'Économie'},
]
DEPARTMENTS = [
    {'name': 'Informatique', 'faculty': 'Sciences'},
    {'name': 'Mathématiques', 'faculty': 'Sciences'},
    {'name': 'Physique', 'faculty': 'Sciences'},
    {'name': 'Français', 'faculty': 'Lettres'},
    {'name': 'Anglais', 'faculty': 'Lettres'},
    {'name': 'Droit privé', 'faculty': 'Droit'},
    {'name': 'Droit public', 'faculty': 'Droit'},
    {'name': 'Gestion', 'faculty': 'Économie'},
    {'name': 'Comptabilité', 'faculty': 'Économie'},
]
PROMOTIONS = ['L1', 'L2', 'L3', 'M1', 'M2']

with app.app_context():
    print('Suppression des tables existantes...')
    db.drop_all()
    print('Création des tables...')
    db.create_all()
    # Rôles
    print('Ajout des rôles...')
    for role_name in ROLES:
        db.session.add(Role(name=role_name))
    db.session.commit()
    print('Suppression des tables existantes...')
    db.drop_all()
    print('Création des tables...')
    db.create_all()
    # Facultés
    faculties = {}
    for f in FACULTIES:
        faculty = Faculty(name=f['name'])
        db.session.add(faculty)
        faculties[f['name']] = faculty
    db.session.commit()
    # Départements
    departments = {}
    for d in DEPARTMENTS:
        faculty = faculties[d['faculty']]
        dept = Department(name=d['name'], faculty_id=faculty.id)
        db.session.add(dept)
        departments[d['name']] = dept
    db.session.commit()
    # Promotions
    for faculty in faculties.values():
        for promo_name in PROMOTIONS:
            promo = Promotion(name=promo_name, faculty_id=faculty.id)
            db.session.add(promo)
    db.session.commit()
    print('Base de données initialisée avec facultés, départements et promotions.')
