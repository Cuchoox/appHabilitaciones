import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Cuchomy1702.@localhost/Mci'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'clave_secreta_super_segura'  # Clave general para Flask
    JWT_SECRET_KEY = 'Mci2024Haru'  # Clave específica para JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)