# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Tests on url path /users/*

import base64
from http import HTTPStatus
import pytest

from brandy.db import create_user, get_db


def basic_auth_header(username, password):
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


class TestIndex:
    @pytest.fixture
    def basic_auth(self, users):
        return lambda u: basic_auth_header(u, users.get(u, ''))

    def test_index(self, basic_auth, client):
        r = client.get('/users/', headers=basic_auth('root'))
        assert r.status_code == HTTPStatus.OK

    def test_forbidden(self, basic_auth, client):
        r = client.get('/users/', headers=basic_auth('alice'))
        assert r.status_code == HTTPStatus.FORBIDDEN

    def test_unauthorized(self, basic_auth, client):
        r = client.get('/users/')
        assert r.status_code == HTTPStatus.UNAUTHORIZED
        assert r.headers['WWW-Authenticate'].startswith('Basic')

    def test_unknown_user(self, basic_auth, client):
        r = client.get('/users/', headers=basic_auth('nosuchuser'))
        assert r.status_code == HTTPStatus.UNAUTHORIZED
        assert r.headers['WWW-Authenticate'].startswith('Basic')


class TestUser:
    @pytest.fixture
    def basic_auth(self, users):
        return lambda u: basic_auth_header(u, users.get(u, ''))

    def test_user(self, basic_auth, client):
        # Bob should be allowed getting /users/bob/ (his own info).
        r = client.get('/users/bob/', headers=basic_auth('bob'))
        assert r.status_code == HTTPStatus.OK

    def test_admin(self, basic_auth, client):
        # Root should be allowed getting /users/bob/.
        r = client.get('/users/bob/', headers=basic_auth('root'))
        assert r.status_code == HTTPStatus.OK

    def test_user_forbidden(self, basic_auth, client):
        # Alice should be denied getting /users/bob/.
        r = client.get('/users/bob/', headers=basic_auth('alice'))
        assert r.status_code == HTTPStatus.FORBIDDEN

    def test_user_unauthorized(self, basic_auth, client):
        r = client.get('/users/bob/')
        assert r.status_code == HTTPStatus.UNAUTHORIZED
        assert r.headers['WWW-Authenticate'].startswith('Basic')
