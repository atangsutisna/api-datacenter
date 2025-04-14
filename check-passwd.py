import bcrypt
import json
import os
import logging

username = input('Enter username: ')
passwd = input('Enter password: ')
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
    print(f"Username '{username}' tidak ditemukan")
else:
    # checking password
    hashed_passwd = found_user['password'].encode('utf-8')
    pass_value = passwd.encode('utf-8')
    if bcrypt.checkpw(pass_value, hashed_passwd):
        print('login success')
        # print(found_user['homedir'])
        dir_list = os.listdir('/home/kangatang/git/filegator/repository' + found_user['homedir'])
        for dir in dir_list:
            print(dir)
    else:
        print('Username atau password tidak cocok')
