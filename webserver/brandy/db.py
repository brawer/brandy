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


@click.command('add-admin')
def add_admin_command():
    """Add a new administrator to the users table."""
    db = get_db()
    username = input('Choose username: ').strip()
    assert re.match(r'^[a-zA-Z]+$', username)
    password = getpass.getpass('Choose password: ')
    create_user(username, password, is_admin=True)
    db.commit()
    click.echo('Created user \"%s\" with admin rights.' % username)


def build_find_features_query(brand_id, bbox=None, limit=None):
    columns = ['f.feature_id', 'f.lng', 'f.lat', 'f.props']
    tables = ['brand_feature AS f']
    conditions, params = ['f.brand_id=?'], [brand_id]
    if bbox != None:
        tables.append('brand_feature_rtree AS r')
        conditions.append('f.internal_id=r.internal_id')
        conditions.append('r.min_lng>=%g' % float(bbox[0]))
        conditions.append('r.max_lng<=%g' % float(bbox[2]))
        conditions.append('r.min_lat>=%g' % float(bbox[1]))
        conditions.append('r.max_lat<=%g' % float(bbox[3]))
        conditions.append('r.brand_id=%d' % brand_id)
    query = 'SELECT %s FROM %s WHERE %s' % (
        ', '.join(columns), ', '.join(tables), ' AND '.join(conditions))
    if limit != None:
        query += ' LIMIT %d' % int(limit)
    return (query, tuple(params))
