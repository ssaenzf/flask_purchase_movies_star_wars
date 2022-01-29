#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, \
    request, url_for, redirect, session
from app.users import usuarioValido, crearUsuario, \
    saldoUsuario, actualizarSaldo, actualizarHistorial
import json
import os
import sys

catalogue_data = open(os.path.join(app.root_path,
                                   'catalogue/catalogue.json'), encoding="utf-8").read()
catalogue = json.loads(catalogue_data)


@app.route('/')
@app.route('/index')
def index():
    print(url_for('static', filename='estilo.css'),
          file=sys.stderr)
    catalogue_data = open(os.path.join(app.root_path,
                                       'catalogue/catalogue.json'),
                          encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    return render_template('ENTRADA_PRINCIPAL.html',
                           title="Home",
                           header="ENTRADA PRINCIPAL",
                           movies=catalogue['peliculas'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    # doc sobre request object en
    # http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
    if request.method == 'GET':
        return render_template('LOG_IN.html',
                               title="Sign In",
                               header="Sign In")

    if request.method == 'POST' and 'username' and 'password' in request.form:
        # aqui se deberia validar con fichero .dat del usuario
        if usuarioValido(request.form) == 1:
            session['user'] = request.form['username']
            session.modified = True
            # se puede usar request.referrer
            # para volver a la pagina desde la que se hizo login
            return redirect(url_for('index'))
        else:

            # aqui se le puede pasar como
            # argumento un mensaje de login invalido
            return render_template('LOG_IN.html',
                                   title="Sign In",
                                   header="Sign In")
    else:
        # se puede guardar la pagina desde la que se invoca 
        session['url_origen'] = request.referrer
        session.modified = True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print(request.referrer, file=sys.stderr)
        return render_template('LOG_IN.html',
                               title="Sign In",
                               header="Sign In")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'user' in session:
        if 'carrito' in session and 'precio' in session:
            session['last_user'] = session['user']
            session['last_carrito'] = session['carrito']
            session['last_precioTotal'] = session['precioTotal']
        session.pop('user', None)
        session.pop('carrito', None)
        session.pop('precioTotal', None)
    session.modified = True
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            try:
                crearUsuario(request.form)
                session['user'] = request.form['username']
                session.modified = True
                return redirect(url_for('index'))
            except Exception:
                return render_template('REGISTRO.html',
                                       title="Sign up",
                                       header="Sign up")

    return render_template('REGISTRO.html',
                           title="Sign up", header="Sign up")


@app.route('/carrito', methods=['GET', 'POST'])
def carrito_usuario():
    if 'user' not in session:
        return render_template('CARRITO_USUARIO.html',
                               title="CARRITO",
                               header="CARRITO",
                               peliculas=catalogue["peliculas"])
    else:
        saldo_restante = saldoUsuario(session['user'])
        print(saldo_restante)
        return render_template('CARRITO_USUARIO.html',
                               title="CARRITO",
                               header="CARRITO",
                               peliculas=catalogue["peliculas"],
                               saldo=float(saldo_restante))


@app.route("/info/<pelicula>", methods=['GET', 'POST'])
def info(pelicula):
    peliculas = catalogue['peliculas']
    for movie in peliculas:
        if movie['titulo'] == pelicula.replace("%20", " "):
            return render_template('pelicula.html',
                                   title="INFO",
                                   header=pelicula.replace("%20", " "),
                                   pelicula=movie)

    return redirect(url_for('index'))


@app.route("/info/anadircarrito/<pelicula>", methods=['GET'])
def anadircarrito(pelicula):
    peliculas = catalogue['peliculas']

    if 'carrito' not in session:
        session['carrito'] = []
        new = {"titulo": pelicula.replace("%20", " "),
               "unidades": 1}
        session['carrito'].append(new)
        for movie in peliculas:
            if movie['titulo'] == pelicula.replace("%20", " "):
                session['precioTotal'] = movie['precio']
        session.modified = True
        return redirect(url_for('index'))
    else:
        for movie in peliculas:
            if movie['titulo'] == pelicula.replace("%20", " "):
                for item in session['carrito']:
                    if item['titulo'] == movie['titulo']:
                        item['unidades'] += 1
                        session['precioTotal'] += movie['precio']
                        return redirect(url_for('index'))

                new = {"titulo": pelicula.replace("%20", " "),
                       "unidades": 1}
                session['carrito'].append(new)
                session['precioTotal'] += movie['precio']
                session.modified = True
                return redirect(url_for('index'))
    session.modified = True
    return redirect(url_for('index'))


@app.route('/info/del/<pelicula>')
def delcarrito(pelicula):

    if 'carrito' not in session or 'precioTotal' not in session:
        return redirect(url_for('index'))

    peliculas = catalogue['peliculas']
    for movie in peliculas:
        if movie['titulo'] == pelicula.replace("%20", " "):
            if 'carrito' in session:
                i = 0
                for item in session['carrito']:
                    if item['titulo'] == pelicula.replace("%20", " "):
                        if (item['unidades'] == 1):
                            del (session['carrito'][i])
                        else:
                            item['unidades'] = item['unidades'] - 1

                        # Modificar dinero del carrito
                        if len(session['carrito']) == 0:
                            session['precioTotal'] = 0
                        else:

                            session['precioTotal'] = \
                                session['precioTotal'] - \
                                movie['precio']
                            if session['precioTotal'] < 0:
                                session['precioTotal'] = 0
                        session.modified = True
                    i = i + 1

                #
    return redirect(url_for('index'))


@app.route('/compracarrito')
def compracarrito():
    if 'user' in session:
        saldo = saldoUsuario(session['user'])
        if float(saldo) > session['precioTotal']:
            saldo = float(saldo) - float(session['precioTotal'])
            actualizarSaldo(session['user'], str(saldo))
            actualizarHistorial(session)
            session['precioTotal'] = 0
            session['carrito'] = []
            session.modified = True
            return redirect(url_for('carrito_usuario'))
        else:
            return redirect(url_for('carrito_usuario'))

    return redirect(url_for('carrito_usuario'))


@app.route('/historial')
def historial():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_path = 'usuarios/' + session['user']
    if not os.path.exists(os.path.join(user_path,
                                       'historial.json')):
        return redirect(url_for('carrito_usuario'))
    historial_data = open(os.path.join(user_path,
                                       'historial.json'),
                          encoding="utf-8").read()
    historial_json = json.loads(historial_data)
    return render_template('HISTORIAL_USUARIO.html',
                           title="HISTORIAL",
                           header="HISTORIAL",
                           historial=historial_json)
