import random
from flask import session

def calcular_oferta(valores_restantes):
    """Calcula la oferta basada en los valores restantes."""
    return sum(valores_restantes) / len(valores_restantes) * random.uniform(0.75, 1.25)

def registrar_partida(username, estado):
    """Registra una partida en la sesión del usuario."""
    partidas = session.setdefault('partidas', {})
    usuario_partidas = partidas.setdefault(username, [])
    usuario_partidas.append({'estado': estado})

def inicializar_juego():
    """Inicializa los valores del juego en la sesión."""
    session['valores'] = [0.01, 1, 5, 10, 25, 50, 75, 100, 200, 300, 400, 500, 750,
                          1000, 5000, 10000, 25000, 50000, 75000, 100000, 200000,
                          300000, 400000, 500000, 750000, 1000000]
    random.shuffle(session['valores'])
    session['valores_restantes'] = session['valores'][:]
    session['maletines'] = list(range(26))
    session['ronda'] = 1
    session['num_maletines'] = 6
    session['maletines_abiertos'] = []
