from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import TypeDecorator, VARCHAR
from datetime import datetime

db = SQLAlchemy()

class GSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    ronda = db.Column(db.Integer, nullable=False)
    num_maletines = db.Column(db.Integer, nullable=False)
    maletin_jugador = db.Column(db.Integer, nullable=False)
    maletines = db.Column(db.PickleType, nullable=False)
    maletines_abiertos = db.Column(db.PickleType, nullable=False)
    maletines_seleccionados = db.Column(db.PickleType, nullable=False)
    valores = db.Column(db.PickleType, nullable=False)
    valores_restantes = db.Column(db.PickleType, nullable=False)
    oferta = db.Column(db.String(50), nullable=True)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
