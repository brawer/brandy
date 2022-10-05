# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Tests on url path /users/*

import pytest
from brandy.db import create_user, get_db


def test_index(client, app):
    with app.app_context():
        create_user('test', 'secret', is_admin=1)
        # TODO: Send an authorized request from this unit test.


def test_index_unauthorized(client):
    response = client.get('/users/')
    assert response.status_code == 401
