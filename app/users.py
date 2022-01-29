import errno
import os
import random
import json
import hashlib


def crearUsuario(form):
    if testForm(form) is False:
        raise Exception()
    else:
        user_path = 'usuarios/' + form['username']

        if os.path.exists(user_path):
            # Exception con mensaje error si se pasa a la función
            print("AY")
            raise Exception()
        else:
            os.mkdir(user_path, 0o777)




        WRITE_FILE = os.path.join(user_path, 'datos.dat')
        file = open(WRITE_FILE, 'w')
        m = hashlib.md5()
        m.update(form['password'].encode('utf-8'))
        file.write(form['username'] + '\n')
        file.write(m.hexdigest() + '\n')
        file.write(form['email'] + '\n')
        file.write(form['tarjeta'] + '\n')
        # dinero en cuenta
        file.write(str(random.randint(0, 1000)))
        file.close()


def usuarioValido(form):
    USER_PATH = 'usuarios/' + form['username'] + '/datos.dat'

    if not os.path.exists(USER_PATH):
        return 0

    m = hashlib.md5()
    m.update(form['password'].encode('utf-8'))
    f = open(USER_PATH, "r")
    usr = f.readline()
    pwd = f.readline()

    if usr.find(form['username']) == -1 or pwd.find(m.hexdigest()) == -1:
        return 0
    return 1

def testForm(form):
    if len(form['username']) == 0 or len(form['password']) == 0 or len(form['email']) == 0 or len(form['tarjeta']) == 0:
        return False
    return True

def saldoUsuario(username):
    USER_PATH = 'usuarios/' + username + '/datos.dat'

    if not os.path.exists(USER_PATH):
        return 0

    f = open(USER_PATH, "r")
    usr = f.readline()
    pwd = f.readline()
    email = f.readline()
    cuenta = f.readline()
    saldo = f.readline()
    f.close()
    return saldo

def actualizarSaldo(username, saldo):
    USER_PATH = 'usuarios/' + username + '/datos.dat'

    if not os.path.exists(USER_PATH):
        return 0

    f = open(USER_PATH, "r")
    usr = f.readline()
    pwd = f.readline()
    email = f.readline()
    cuenta = f.readline()
    f.close()
    f = open(USER_PATH, "w")
    f.write(usr)
    f.write(pwd)
    f.write(email)
    f.write(cuenta)
    # dinero en cuenta
    f.write(saldo)
    f.close()

def actualizarHistorial(session):
    user_path = 'usuarios/' + session['user']
    HISTORIAL_FILE = os.path.join(user_path, 'historial.json')
    if not os.path.exists(HISTORIAL_FILE):
        file = open(HISTORIAL_FILE, 'w')
        historial = []
        peliculas = session['carrito']
        info = {"id": len(historial), "peliculas": peliculas,
                "precio": session['precioTotal']}
        historial.append(info)
        json.dump(historial, file)
    else:
        file = open(HISTORIAL_FILE, 'r+')
        a = json.load(file)
        info = {"id": len(a), "peliculas": session['carrito'],
                "precio": session['precioTotal']}
        a.append(info)
        file.seek(0)
        file.truncate()
        json.dump(a, file)
        