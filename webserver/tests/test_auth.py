# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Unittests on authentication helpers

import pytest

import brandy.auth
from brandy.db import create_user, get_db


def test_get_user_roles(app):
    with app.app_context():
        create_user('admin', 'admin-pass', is_admin=True)
        create_user('foo', 'foo-pass', is_admin=False)
        assert brandy.auth.get_user_roles('admin') == ['admin']
        assert brandy.auth.get_user_roles('foo') == []
        assert brandy.auth.get_user_roles('nosuchuser') == []


def test_verify_password(app):
    with app.app_context():
        assert brandy.auth.verify_password('nosuchuser', 'secret') == None

        create_user('kim', 'kim-password')
        assert brandy.auth.verify_password('kim', 'kim-password') == 'kim'
        assert brandy.auth.verify_password('kim', 'bad-password') == None
