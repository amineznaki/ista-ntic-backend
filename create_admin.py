# Script simple pour créer / mettre à jour l'admin. Utilise la variable d'environnement ADMIN_PASSWORD.
import os
import sys
import time
from models import db, Admin
from werkzeug.security import generate_password_hash
from app import create_app
from sqlalchemy.exc import OperationalError

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
MAX_RETRIES = 5
RETRY_DELAY = 2

for attempt in range(MAX_RETRIES):
    try:
        app = create_app()
        with app.app_context():
            db.create_all()
            admin = Admin.query.filter_by(username='admin').first()
            if not admin:
                admin = Admin(username='admin', password_hash=generate_password_hash(ADMIN_PASSWORD))
                db.session.add(admin)
                db.session.commit()
                print(f'✓ Admin créé avec le mot de passe: {ADMIN_PASSWORD}')
            else:
                # Mettre à jour le mot de passe si diffère
                admin.password_hash = generate_password_hash(ADMIN_PASSWORD)
                db.session.commit()
                print(f'✓ Mot de passe admin mis à jour: {ADMIN_PASSWORD}')
            break  # Success, exit retry loop
    except OperationalError as e:
        if attempt < MAX_RETRIES - 1:
            print(f'⚠ Tentative {attempt + 1}/{MAX_RETRIES}: Base de données non prête, nouvelle tentative dans {RETRY_DELAY}s...')
            time.sleep(RETRY_DELAY)
        else:
            print(f'✗ Erreur: Impossible de se connecter à la base de données après {MAX_RETRIES} tentatives: {e}', file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f'✗ Erreur lors de la création de l\'admin: {e}', file=sys.stderr)
        sys.exit(1)
