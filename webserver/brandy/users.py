# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Flask blueprint for handling /users/*

import flask
import json
from werkzeug.exceptions import NotFound

from brandy.auth import auth
from brandy.db import get_db

bp = flask.Blueprint('users', __name__, url_prefix='/users')


@bp.route('/')
@auth.login_required(role='admin')
def index():
    db = get_db()
    users = db.execute(
        'SELECT id, username, is_admin FROM user ORDER BY username'
    ).fetchall()
    return [_user_to_json(u) for u in users]


@bp.route('/<username>/')
@auth.login_required(role='admin')
def user(username):
    db = get_db()
    user = db.execute(
        'SELECT id, username, is_admin FROM user WHERE username = ?',
        (username,)
    ).fetchone()
    if user is None:
        raise NotFound()
    return _user_to_json(user)


def _user_to_json(user):
    return {
        'id': user['id'],
        'username': user['username'],
        'is_admin': (user['is_admin'] != 0)
    }
