from flask import Flask, jsonify, request, abort, make_response, session
import os
import json
import bcrypt

app = Flask(__name__)
app.secret_key = 'datacenter2025'

@app.route("/")
def home():
    return jsonify({'message': 'Welcome to datacenter!'})

@app.route("/ls")
def viewPubFiles():
    dir_list = os.listdir('/home/kangatang/git/filegator/repository/sdd/Public Internal')
    print(dir_list)
    return jsonify({'files': dir_list})

@app.route("/users")
def viewUsers():
    with open('/home/kangatang/git/filegator/private/users.json', 'r', encoding='utf-8') as file:
        users = json.load(file)
    return jsonify(users)

@app.route("/login", methods=['POST'])
def doLogin():
    username = request.json.get('username')
    passwd = request.json.get('password')
    if username is None or passwd is None:
        abort(400)
    with open('/home/kangatang/git/filegator/private/users-prd.json', 'r', encoding='utf-8') as file:
        users = json.load(file)

    # checking password
    found_user = None
    for user_id, user_data in users.items():
        if user_data["username"] == username:
            found_user = user_data
            break
    if not found_user:    
        return make_response(jsonify({'message': 'Data tidak ditemukan'}), 400)

    # checking password
    hashed_passwd = found_user['password'].encode('utf-8')
    pass_value = passwd.encode('utf-8')
    if bcrypt.checkpw(pass_value, hashed_passwd):
        return make_response(jsonify({'message': 'Login sukses'}), 200)
    else:
        return make_response(jsonify({'message': 'Username atau password tidak cocok'}), 400)
