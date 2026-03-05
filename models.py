from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
import secrets # Pour la génération de codes MFA

db = SQLAlchemy()


inscriptions = db.Table('inscriptions',
    db.Column('etudiant_id', db.Integer, db.ForeignKey('utilisateur.id', ondelete='CASCADE'), primary_key=True),
    db.Column('cours_id', db.Integer, db.ForeignKey('cours.id', ondelete='CASCADE'), primary_key=True)
)

# Table Utilisateur

class Utilisateur(UserMixin, db.Model):
    __tablename__ = 'utilisateur'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum('etudiant', 'enseignant', 'admin'), default='etudiant', nullable=False)
    photo = db.Column(db.String(255), nullable=True)

    
    mfa_secret = db.Column(db.String(16), nullable=True) # Clé secrète pour Google Authenticator
    mfa_enabled = db.Column(db.Boolean, default=False) # Si le MFA est activé pour l'utilisateur

    
    cours = db.relationship('Cours', backref='enseignant', lazy=True, cascade='all, delete-orphan')
    examens = db.relationship('Examen', backref='etudiant', lazy=True, cascade='all, delete-orphan')
    resultats = db.relationship('Resultat', backref='etudiant', lazy=True, cascade='all, delete-orphan')
    plaintes = db.relationship('Plainte', backref='etudiant', lazy=True, cascade='all, delete-orphan')

    
    cours_inscrits = db.relationship(
        'Cours',
        secondary=inscriptions, # Utilisation de la table d'association définie ci-dessus
        backref=db.backref('etudiants', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Utilisateur {self.email}>'

    # Méthodes pour MFA (seront utilisées dans les routes d'authentification)
    def generate_mfa_secret(self):
        self.mfa_secret = secrets.token_hex(8) # Génère une clé hexadécimale de 16 caractères
        self.mfa_enabled = True
        db.session.add(self)
        db.session.commit()
        return self.mfa_secret

    def disable_mfa(self):
        self.mfa_secret = None
        self.mfa_enabled = False
        db.session.add(self)
        db.session.commit()

#  Table des promotions (BAC1 à BAC4)
class Promotion(db.Model):
    __tablename__ = 'promotion'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True, nullable=False)
    # Si une promotion est supprimée, ses cours associés sont supprimés en cascade.
    cours = db.relationship('Cours', backref='promotion_obj', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Promotion {self.nom}>'

#  Table des cours
class Cours(db.Model):
    __tablename__ = 'cours'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    type = db.Column(db.Enum('pdf', 'video'), nullable=False) # 'pdf' ou 'video'
    fichier = db.Column(db.String(255), nullable=False) # Nom du fichier principal du cours
    enseignant_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id', ondelete='CASCADE'), nullable=False)
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotion.id', ondelete='CASCADE'), nullable=False)
    date_publication = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations avec suppressions en cascade
    # Si un cours est supprimé, ses examens, questions et éléments de playlist sont supprimés.
    examens = db.relationship('Examen', backref='cours', lazy=True, cascade='all, delete-orphan')
    questions = db.relationship('Question', backref='cours', lazy=True, cascade='all, delete-orphan')
    playlist = db.relationship('Playlist', backref='cours', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Cours {self.titre}>'

#  Table pour les fichiers complémentaires (playlist)
class Playlist(db.Model):
    __tablename__ = 'playlist'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    fichier = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum('pdf', 'video'), nullable=False)
    cours_id = db.Column(db.Integer, db.ForeignKey('cours.id', ondelete='CASCADE'), nullable=False)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Playlist {self.titre}>'

#  Table des examens
class Examen(db.Model):
    __tablename__ = 'examen'

    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id', ondelete='CASCADE'), nullable=False)
    cours_id = db.Column(db.Integer, db.ForeignKey('cours.id', ondelete='CASCADE'), nullable=False)
    date_passage = db.Column(db.DateTime, default=datetime.utcnow)
    score_obtenu = db.Column(db.Integer, nullable=False, default=0) 
    temps_pris_secondes = db.Column(db.Integer, nullable=False, default=0) 

    
    questions = db.relationship('Question', backref='examen', lazy=True, cascade='all, delete-orphan')
    resultat = db.relationship('Resultat', backref='examen', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Examen {self.id}>'

#  Table des questions
class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    texte = db.Column(db.Text, nullable=False)
    examen_id = db.Column(db.Integer, db.ForeignKey('examen.id', ondelete='SET NULL'), nullable=True) 
    cours_id = db.Column(db.Integer, db.ForeignKey('cours.id', ondelete='CASCADE'), nullable=False) 

    choix_1 = db.Column(db.String(255), nullable=False)
    choix_2 = db.Column(db.String(255), nullable=False)
    choix_3 = db.Column(db.String(255), nullable=False)
    bonne_reponse = db.Column(db.String(255), nullable=False) 

    def __repr__(self):
        return f'<Question {self.id}>'

#  Table des résultats
class Resultat(db.Model):
    __tablename__ = 'resultat'

    id = db.Column(db.Integer, primary_key=True)
    examen_id = db.Column(db.Integer, db.ForeignKey('examen.id', ondelete='CASCADE'), nullable=False, unique=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id', ondelete='CASCADE'), nullable=False)
    cours_id = db.Column(db.Integer, db.ForeignKey('cours.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    valide = db.Column(db.Boolean, default=False)
    date_validation = db.Column(db.DateTime, default=datetime.utcnow)
    duree_examen_secondes = db.Column(db.Integer, nullable=False, default=0) 


    def __repr__(self):
        return f'<Resultat {self.id}>'

#  Table des plaintes ou problèmes déclarés
class Plainte(db.Model):
    __tablename__ = 'plainte'

    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id', ondelete='CASCADE'), nullable=False)
    sujet = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.Enum('non traité', 'en cours', 'résolu'), default='non traité', nullable=False)

    def __repr__(self):
        return f'<Plainte {self.id}>'




