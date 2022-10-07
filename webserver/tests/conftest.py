# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

import os
import tempfile

import pytest
from brandy import create_app
from brandy.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    # Using a sqlite3 in-memory database (":memory:") would be faster,
    # but Flask does not make this easy; beware of threading issues.
    # https://gehrcke.de/2015/05/in-memory-sqlite-database-and-flask-a-threading-trap/
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'APPLICATION_ROOT': 't',
        'DATABASE': db_path,
        'PREFERRED_URL_SCHEME': 'https',
        'TESTING': True,
        'SERVER_NAME': 'brandy.test'
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
