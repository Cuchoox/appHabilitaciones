import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Cucho123@localhost/Mci'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'clave_secreta_super_segura'  # Clave general para Flask
    JWT_SECRET_KEY = 'Mci2024Haru'  # Clave específica para JWT
