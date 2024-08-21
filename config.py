import os

class Config:
    SECRET_KEY = 'secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Puedes cambiar a PostgreSQL o cualquier otra base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False