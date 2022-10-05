# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

from brandy.db import get_db

auth = HTTPBasicAuth()

@auth.get_user_roles
def get_user_roles(user):
    db = get_db()
    capabilities = db.execute(
        'SELECT is_admin FROM user WHERE username = ?',
        (user,)
    ).fetchone()
    if capabilities is None:
        return []
    roles = []
    if capabilities['is_admin'] != 0:
        roles.append('admin')
    return roles


@auth.verify_password
def verify_password(username, password):
    db = get_db()
    user = db.execute(
        'SELECT password FROM user WHERE username = ?',
        (username,)
    ).fetchone()
    if user != None and check_password_hash(user['password'], password):
        return username
    else:
        return None
