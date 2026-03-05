import os

class Config:
    # Configuration de la base de données MySQL
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/validations"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clé secrète pour les sessions Flask
    SECRET_KEY = '9f1a8c5bdcc4880efcd8a51cb84a1baf6230ccf6673e3b003eb116e9920fa0c3'

    # Configuration du JWT
    JWT_SECRET_KEY = '9f1a8c5bdcc4880efcd8a51cb84a1baf6230ccf6673e3b003eb116e9920fa0c3'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Durée de vie en secondes (1h)
    JWT_TOKEN_LOCATION = ['headers']  # Important pour éviter le KeyError
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
  # Limite de 100Mo pour les uploads













