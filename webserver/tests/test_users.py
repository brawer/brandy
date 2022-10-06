# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Tests on url path /users/*

import base64
from http import HTTPStatus
import pytest

from brandy.db import create_user, get_db


def basic_auth(username, password):
    cred = '%s:%s' % (username, password)
    cred = base64.b64encode(cred.encode('utf-8')).decode('utf-8')
    return {'Authorization': 'Basic %s' % cred}


@pytest.fixture
def users(app):
    p = {'root': 'rootpass', 'alice': 'wonderland', 'bob': 'bassword'}
    with app.app_context():
        for username, password in p.items():
            create_user(username, password, is_admin=(username == 'root'))
        get_db().commit()
    return p


def test_index(client, users):
    r = client.get('/users/', headers=basic_auth('root', 'rootpass'))
    assert r.status_code == HTTPStatus.OK


def test_index_forbidden(client, users):
    r = client.get('/users/', headers=basic_auth('alice', 'wonderland'))
    assert r.status_code == HTTPStatus.FORBIDDEN


def test_index_unauthorized(client):
    r = client.get('/users/')
    assert r.status_code == HTTPStatus.UNAUTHORIZED
    assert r.headers['WWW-Authenticate'].startswith('Basic')


def test_index_unknown_user(client):
    r = client.get('/users/', headers=basic_auth('nosuchuser', 'secret'))
    assert r.status_code == HTTPStatus.UNAUTHORIZED
    assert r.headers['WWW-Authenticate'].startswith('Basic')


def test_user(client, users):
    r = client.get('/users/alice/', headers=basic_auth('root', 'rootpass'))
    assert r.status_code == HTTPStatus.OK
