from flask import Flask, render_template, request, session, make_response, jsonify
from threading import Thread
from flask_socketio import SocketIO, emit
from threading import Thread
import sqlite3



app = Flask('app')
app.config['SECRET_KEY'] = 'qQw_90cRT'
socketio = SocketIO(app, allow_unsafe_werkzeug=True)

connection = sqlite3.connect("userBaze.db", check_same_thread=False)
cursor = connection.cursor()
#
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS Users (
# id INTEGER PRIMARY KEY,
# username TEXT NOT NULL,
# mail TEXT NOT NULL,
# levl INTEGER,
# exp INTEGER,
# max_win FLOAT,
# kol_games INTEGER,
# all_win FLOAT,
# win INTEGER,
# lose INTEGER,
# gecpots FLOAT,
# balance FLOAT,
# password TEXT
# )
# ''')
#connection.commit()

@app.route('/games')
def games_show():
    return render_template("games_all.html")

@app.route('/profile_go')
def go_profile():
    return render_template("setings.html")

@app.route('/registretion')
def registretion():
    _name = request.cookies.get('name')
    _password = request.cookies.get('password')

    cursor.execute("SELECT id, username, password FROM Users WHERE username = ?", (_name,))
    user_data = cursor.fetchone()
    if user_data == None or user_data[2] != _password:
        resp = make_response(render_template('registration.html'))
        resp.delete_cookie('name')
        resp.delete_cookie('password')
        return resp
    else:
        return render_template("games_all.html")

@app.route('/')
def login():
    _name = request.cookies.get('name')
    _password = request.cookies.get('password')
    cursor.execute("SELECT id, username, password FROM Users WHERE username = ?", (_name,))
    user_data = cursor.fetchone()
    if user_data == None or user_data[2] != _password:
        resp = make_response(render_template('vhod.html'))
        resp.delete_cookie('name')
        resp.delete_cookie('password')
        return resp
    else:
        return render_template("games_all.html")


@app.route('/ruletka')
def ruletka_game():
    _name = request.cookies.get('name')
    _password = request.cookies.get('password')

    cursor.execute("SELECT id, username, password FROM Users WHERE username = ?", (_name,))
    user_data = cursor.fetchone()
    if user_data == None or user_data[2] != _password:
        resp = make_response(render_template('vhod.html'))
        resp.delete_cookie('name')
        resp.delete_cookie('password')
        return resp

    return render_template("ruletka.html")

@app.route('/api/data_vhod', methods=['POST', 'GET'])
def vhod_api():
    _name = request.cookies.get('name')
    _password = request.cookies.get('password')

    cursor.execute("SELECT id, username, password FROM Users WHERE username = ?", (_name,))
    user_data = cursor.fetchone()
    if _name != None or user_data == None or user_data['password'] != _password:
        pass
    else:
        return render_template("games_all.html")

    data = request.get_json()

    cursor.execute("SELECT id, username, password FROM Users WHERE username = ?", (data['name'],))
    user_data = cursor.fetchone()
    if user_data != None:
        if data['passwd'] == user_data[2]:
            response_data = {'url': '/games'}
            return jsonify(response_data)

    response_data = {'message': 'Data received successfully!', 'received_key': data['key']}
    return jsonify(response_data)

@app.route('/api/data_reg', methods=['POST', 'GET'])
def reg_api():
    _name = request.cookies.get('name')
    _password = request.cookies.get('password')

    cursor.execute("SELECT id, username, password FROM Users WHERE username = ?", (_name,))
    user_data = cursor.fetchone()
    if _name != None or user_data == None or user_data['password'] != _password:
        pass
    else:
        return render_template("games_all.html")

    data = request.get_json()
    cursor.execute("SELECT id, username, password FROM Users WHERE username = ?", (data['name'],))
    user_data = cursor.fetchone()
    if user_data == None:
        f = open("id_chek", "r")
        num = int(f.read())
        f.close()
        num += 1
        f = open("id_chek", "w")
        f.write(str(num))
        f.close()
        cursor.execute('INSERT INTO Users (id, username, mail, levl, exp, max_win, kol_games, all_win, win, lose, gecpots, balance, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (f'{num}', data['name'], "", 0, 0, 0.0, 0, 0.0, 0, 0, 0, 0.0, str(data['passwd'])))
        connection.commit()
        response_data = {'url': '/games'}
        return jsonify(response_data)

    response_data = {'message': 'Data received successfully!', 'received_key': data['key']}
    return jsonify(response_data)

@app.route('/api/get_balance', methods=['POST', 'GET'])
def get_balance_api():
    _name = request.cookies.get('name')
    _password = request.cookies.get('password')

    cursor.execute("SELECT id, username, password, balance FROM Users WHERE username = ?", (_name,))
    user_data = cursor.fetchone()
    if _name != None or user_data == None or user_data['password'] != _password:
        pass
    else:
        return render_template("games_all.html")

    data = request.get_json()
    cursor.execute("SELECT id, username, password, balance FROM Users WHERE username = ?", (data['name'],))
    user_data = cursor.fetchone()
    if user_data != None:
        if data['passwd'] == user_data[2]:
            response_data = {'balance': user_data[3]}
            return jsonify(response_data)

    return render_template("vhod.html")

@app.route('/api/save_balance', methods=['POST', 'GET'])
def save_balance_api():
    _name = request.cookies.get('name')
    _password = request.cookies.get('password')

    cursor.execute("SELECT id, username, password, balance FROM Users WHERE username = ?", (_name,))
    user_data = cursor.fetchone()
    if _name != None or user_data == None or user_data['password'] != _password:
        pass
    else:
        return render_template("games_all.html")

    data = request.get_json()
    cursor.execute("SELECT id, username, password, balance FROM Users WHERE username = ?", (data['name'],))
    user_data = cursor.fetchone()
    if user_data != None:
        if data['passwd'] == user_data[2]:
            __balance = user_data[3] + data['bal']
            cursor.execute('UPDATE Users SET balance = ? WHERE username = ?', (__balance, _name))
            connection.commit()

            response_data = {'operation': "success"}
            return jsonify(response_data)

    return render_template("vhod.html")

def run():
    app.run(host="0.0.0.0", port=8820)

def start_server():
    server = Thread(target=run)
    server.start()

def keep_alive():
    socketio.run(app, allow_unsafe_werkzeug=True, host="0.0.0.0", port=8820)

if __name__ == "__main__":
    keep_alive()
