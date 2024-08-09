from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import random

app = Flask(__name__)
app.secret_key = 'secret_key'

def calcular_oferta(valores_restantes):
    return sum(valores_restantes) / len(valores_restantes) * random.uniform(0.75, 1.25)

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
        if username in session.get('usuarios', {}):
            flash('El usuario ya existe.', 'error')
        else:
            session.setdefault('usuarios', {})[username] = generate_password_hash(password)
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
        session['valores'] = [0.01, 1, 5, 10, 25, 50, 75, 100, 200, 300, 400, 500, 750,
                              1000, 5000, 10000, 25000, 50000, 75000, 100000, 200000,
                              300000, 400000, 500000, 750000, 1000000]
        random.shuffle(session['valores'])
        session['maletin_jugador'] = int(request.form['maletin']) - 1
        session['valores_restantes'] = session['valores'][:]
        session['valores_restantes'].pop(session['maletin_jugador'])
        session['maletines'] = list(range(26))
        session['maletines'].remove(session['maletin_jugador'])
        session['ronda'] = 1
        session['num_maletines'] = 6
        session['maletines_abiertos'] = []
        return redirect(url_for('game'))

    return render_template('select_maletin.html')

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

        session['num_maletines'] -= len(seleccionados)

        if session['num_maletines'] == 0:
            session['ronda'] += 1
            if session['ronda'] <= 5:
                session['num_maletines'] = 6 - session['ronda'] + 1
            else:
                session['num_maletines'] = 1

            if session['ronda'] > 10:
                return redirect(url_for('final'))

            oferta = calcular_oferta(session['valores_restantes'])
            session['oferta'] = f"{oferta:,.2f}"

            return render_template('offer.html', oferta=session['oferta'], maletines_abiertos=session['maletines_abiertos'])

    return render_template('game.html', ronda=session['ronda'], num_maletines=session['num_maletines'], maletines=session['maletines'], maletines_abiertos=session['maletines_abiertos'])


@app.route('/offer', methods=['POST'])
def offer():
    if 'username' not in session:
        return redirect(url_for('login'))
       
    decision = request.form['decision']
    if decision == 'deal':
        return render_template('result.html', result=f"Ha aceptado la oferta de ${session['oferta']}.")
    else:
        if session['ronda'] > 10:
            return redirect(url_for('final'))
        else:
            return redirect(url_for('game'))

@app.route('/final', methods=['GET', 'POST'])
def final():
    if 'username' not in session:
        return redirect(url_for('login'))

    maletin_jugador_valor = session['valores'][session['maletin_jugador']]
    ultimo_valor = session['valores_restantes'][0] if session.get('final_decision') == 'switch' else maletin_jugador_valor

    if request.method == 'POST':
        decision = request.form['final_decision']
        if decision == 'switch':
            final_valor = session['valores_restantes'][0]
        else:
            final_valor = maletin_jugador_valor

        registrar_partida(session['username'], 'Finalizada')

        return render_template('result.html', result=f"Usted ha ganado ${final_valor:,.2f}.",
                               maletin_jugador_valor=maletin_jugador_valor,
                               ultimo_valor=ultimo_valor)

    return render_template('final.html', maletin_jugador_valor=maletin_jugador_valor, ultimo_valor=ultimo_valor)

@app.route('/partidas')
def partidas():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    partidas_usuario = session.get('partidas', {}).get(session['username'], [])
    return render_template('partidas.html', partidas=partidas_usuario)

if __name__ == '__main__':
    app.run(debug=True)
