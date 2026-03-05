from flask import Flask, redirect
from config import Config
from models import db, Utilisateur
#from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import os

# Initialisation de l'application
app = Flask(__name__)
app.config.from_object(Config)

# Initialisation des extensions
db.init_app(app)
#migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Redirection si utilisateur non connecté
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."

# Fonction pour charger un utilisateur depuis son ID
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Utilisateur, int(user_id))


@app.template_filter('localtime')
def format_datetime_filter(value, format="%d/%m/%Y %H:%M"):
    """
    Formate un objet datetime en une chaîne de caractères lisible localement.
    Si la valeur est None, retourne une chaîne vide ou "N/A".
    """
    if value is None:
        return "N/A"
    return value.strftime(format)

# --- FIN DE L'AJOUT DU FILTRE ---
# Création des tables + création de l’admin par défaut
with app.app_context():
    db.create_all()

    admin = Utilisateur.query.filter_by(role='admin').first()
    if not admin:
        admin = Utilisateur(
            nom='Admin',
            prenom='Principal',
            email='admin@umk.com',
            mot_de_passe=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

# Routes
@app.route('/')
def index():
    return redirect('/login')

# Enregistrement des Blueprints
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.admin import admin_bp
from routes.teacher_routes import teacher_bp
from routes.etudiant_routes import etudiant_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(etudiant_bp)

# Création du dossier de téléchargement s'il n'existe pas
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run( debug=True)
    