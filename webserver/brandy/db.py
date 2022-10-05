# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

import getpass
import re
import sqlite3

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(add_admin_command)


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def create_user(username, password, is_admin=False):
    password_hash = generate_password_hash(password)
    db = get_db()
    db.execute('INSERT INTO user (username, password, is_admin)'
               ' VALUES (?, ?, ?)',
               (username, password_hash, (1 if is_admin else 0)))
    db.commit()


@click.command('add-admin')
def add_admin_command():
    """Add a new administrator to the users table."""
    db = get_db()
    username = input('Choose username: ').strip()
    assert re.match(r'^[a-zA-Z]+$', username)
    password = getpass.getpass('Choose password: ')
    create_user(username, password, is_admin=True)
    click.echo('Created user \"%s\" with admin rights.' % username)
