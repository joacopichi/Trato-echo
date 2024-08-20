from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from utiles import calcular_oferta, inicializar_juego
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('select_maletin'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usuarios = session.setdefault('usuarios', {})

        if username in usuarios:
            flash('El usuario ya existe.', 'error')
        else:
            usuarios[username] = generate_password_hash(password)
            flash('Registro exitoso. Puedes iniciar sesión ahora.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usuarios = session.get('usuarios', {})

        if username in usuarios and check_password_hash(usuarios[username], password):
            session['username'] = username
            return redirect(url_for('select_maletin'))
        flash('Nombre de usuario o contraseña incorrectos.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/select_maletin', methods=['GET', 'POST'])
def select_maletin():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        inicializar_juego()
        maletin_jugador = int(request.form['maletin']) - 1

        session['maletin_jugador'] = maletin_jugador
        session['valores_restantes'].pop(maletin_jugador)
        session['maletines'].remove(maletin_jugador)
        session['maletines_seleccionados'] = [maletin_jugador]

        return redirect(url_for('game'))

    partidas_guardadas = session.get('partidas', {}).get(session['username'], [])

    return render_template('select_maletin.html', partidas_guardadas=partidas_guardadas)

def registrar_partida(username, estado, eliminar=False):
    """Registra una partida en la sesión del usuario."""
    partidas = session.setdefault('partidas', {})
    usuario_partidas = partidas.setdefault(username, [])

    if eliminar:
        if usuario_partidas:
            usuario_partidas.pop()
        session['partidas'] = partidas
        return

    num_partida = len(usuario_partidas) + 1
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_partida = f"Partida {num_partida} - {fecha_hora}"

    partida = {
        'nombre': nombre_partida,
        'estado': estado,
        'ronda': session.get('ronda'),
        'num_maletines': session.get('num_maletines'),
        'maletin_jugador': session.get('maletin_jugador'),
        'maletines': session.get('maletines'),
        'maletines_abiertos': session.get('maletines_abiertos'),
        'maletines_seleccionados': session.get('maletines_seleccionados'),
        'valores': session.get('valores'),
        'valores_restantes': session.get('valores_restantes'),
        'oferta': session.get('oferta')
    }

    usuario_partidas.append(partida)
    session['partidas'] = partidas

@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        seleccionados = [int(x) - 1 for x in request.form.getlist('maletines')]
        
        if len(seleccionados) != session['num_maletines']:
            flash(f"Debe seleccionar exactamente {session['num_maletines']} maletines.", 'error')
            return redirect(url_for('game'))

        for maletin in seleccionados:
            if maletin in session['maletines']:
                valor = session['valores'][maletin]
                session['valores_restantes'].remove(valor)
                session['maletines'].remove(maletin)
                session['maletines_abiertos'].append((maletin + 1, valor))
                session['maletines_seleccionados'].append(maletin)

        session['num_maletines'] -= len(seleccionados)

        if session['num_maletines'] == 0:
            session['ronda'] += 1
            session['num_maletines'] = max(1, 6 - session['ronda'] + 1)

            if session['ronda'] > 10:
                return redirect(url_for('final'))

            session['oferta'] = f"{calcular_oferta(session['valores_restantes']):,.2f}"
            return render_template('offer.html', oferta=session['oferta'], maletines_abiertos=session['maletines_abiertos'])

    return render_template('game.html', ronda=session['ronda'], num_maletines=session['num_maletines'], maletines=session['maletines'], maletines_abiertos=session['maletines_abiertos'])

@app.route('/offer', methods=['POST'])
def offer():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    decision = request.form['decision']
    if decision == 'deal':
        maletin_jugador_valor = session['valores'][session['maletin_jugador']]
        oferta_aceptada = session['oferta']
        registrar_partida(session['username'], 'Finalizada', eliminar=True)
        return render_template('result.html', 
                               result=f"Ha aceptado la oferta de ${oferta_aceptada}.")
    return redirect(url_for('final' if session['ronda'] > 10 else 'game'))

@app.route('/final', methods=['GET', 'POST'])
def final():
    if 'username' not in session:
        return redirect(url_for('login'))

    valores = session['valores']
    maletin_jugador_valor = valores[session['maletin_jugador']]

    valores_seleccionados = [valores[i] for i in session.get('maletines_seleccionados', [])]
    valores_faltantes = [v for v in valores if v not in valores_seleccionados]

    maletin_no_seleccionado_valor = valores_faltantes[0] if len(valores_faltantes) == 1 else None

    if request.method == 'POST':
        decision = request.form['final_decision']
        if decision == 'switch' and maletin_no_seleccionado_valor is not None:
            maletin_final_valor = maletin_no_seleccionado_valor
        else:
            maletin_final_valor = maletin_jugador_valor

        registrar_partida(session['username'], 'Finalizada', eliminar=True)

        return render_template('result.html', 
                               result=f"Usted ha ganado ${maletin_final_valor:,.2f}.",
                               maletin_final_valor=f"${maletin_final_valor:,.2f}",
                               maletin_no_seleccionado_valor=f"${maletin_no_seleccionado_valor:,.2f}" if maletin_no_seleccionado_valor is not None else "No disponible")

    return render_template('final.html')

@app.route('/guardar_partida', methods=['POST'])
def guardar_partida():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    registrar_partida(session['username'], 'Pendiente')
    flash('Partida guardada con éxito.', 'success')
    return redirect(url_for('index'))

@app.route('/continuar_partida', methods=['POST'])
def continuar_partida():
    if 'username' not in session:
        return redirect(url_for('login'))

    partida_id = int(request.form['partida_id'])
    partidas = session.get('partidas', {}).get(session['username'], [])
    
    if partida_id < len(partidas):
        partida = partidas[partida_id]
        session.update(partida)  
        return redirect(url_for('game'))

    flash('La partida seleccionada no existe o no es válida.', 'error')
    return redirect(url_for('select_maletin'))

@app.route('/partidas', methods=['GET', 'POST'])
def partidas():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    partidas_usuario = session.get('partidas', {}).get(session['username'], [])

    if request.method == 'POST':
        partida_index = int(request.form['partida'])
        partida_seleccionada = partidas_usuario[partida_index]

        session['ronda'] = partida_seleccionada['ronda']
        session['num_maletines'] = partida_seleccionada['num_maletines']
        session['maletin_jugador'] = partida_seleccionada['maletin_jugador']
        session['maletines'] = partida_seleccionada['maletines']
        session['maletines_abiertos'] = partida_seleccionada['maletines_abiertos']
        session['maletines_seleccionados'] = partida_seleccionada['maletines_seleccionados']
        session['valores'] = partida_seleccionada['valores']
        session['valores_restantes'] = partida_seleccionada['valores_restantes']
        session['oferta'] = partida_seleccionada['oferta']

        return redirect(url_for('game'))

    return render_template('partidas.html', partidas=partidas_usuario)

if __name__ == '__main__':
    app.run(debug=True)
    
