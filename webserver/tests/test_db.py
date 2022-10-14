# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

import pytest
import sqlite3

from brandy.db import get_db, build_find_features_query

# Within an application context, get_db should return
# the same connection each time it’s called. After the context,
# the connection should be closed.
def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    assert 'closed' in str(e.value)


# The init-db command should call the init_db function and output a message.
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
    def fake_init_db():
        Recorder.called = True
    monkeypatch.setattr('brandy.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called


def test_build_find_features_query():
    t = lambda x: x[0].replace('?', '%s') % x[1]
    assert t(build_find_features_query(7272, bbox=None, limit=None)) == (
        'SELECT f.feature_id, f.lng, f.lat, f.props'
        ' FROM brand_feature AS f WHERE f.brand_id=7272')
    assert t(build_find_features_query(7272, bbox=None, limit=10)) == (
        'SELECT f.feature_id, f.lng, f.lat, f.props'
        ' FROM brand_feature AS f WHERE f.brand_id=7272'
        ' LIMIT 10')
    assert t(build_find_features_query(7272, bbox=(1.1, 2.2, 3.3, 4.4), limit=10)) == (
        'SELECT f.feature_id, f.lng, f.lat, f.props'
        ' FROM brand_feature AS f, brand_feature_rtree AS r'
        ' WHERE f.brand_id=7272 AND f.internal_id=r.internal_id'
        ' AND r.min_lng>=1.1 AND r.max_lng<=3.3'
        ' AND r.min_lat>=2.2 AND r.max_lat<=4.4'
        ' AND r.brand_id=7272'
        ' LIMIT 10')
