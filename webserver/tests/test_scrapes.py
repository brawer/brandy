# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Tests on url path /scrapes/*

import pytest
from brandy.db import get_db


def test_index(client):
    response = client.get('/scrapes/')
    assert response.status_code == 200
    assert b'Q860_foobar.py' in response.data
    assert b'/scrapes/17/' in response.data


def test_scrape(client):
    response = client.get('/scrapes/17/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Q860_foobar.py' in html
    assert '821' in html


def test_scrape_not_found(client):
    response = client.get('/scrapes/13/')
    assert response.status_code == 404


def test_scrape_upload_get(client):
    response = client.get('/scrapes/upload')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'method="post"' in html
    assert 'Upload' in html


def test_scrape_upload_post(client, app):
    response = client.post('/scrapes/upload', data={
      'scraper': 'Q1227164_fust.py',
      'data': '{"type": "FeatureCollection", "features": [{},{},{}]}',
      'error_log': 'log\nwith multiple lines and "quotes"'
    })
    assert response.status_code == 201
    assert response.headers['Location'] == '/scrapes/24/'
    html = response.get_data(as_text=True)
    assert '<meta http-equiv="refresh" content="0; url=\'/scrapes/24/\'" />' \
        in html
    with app.app_context():
        row = get_db().execute(
            'SELECT scraper, num_features, error_log'
            ' FROM scrape'
            ' WHERE id = 24',
        ).fetchone()
    assert row is not None
    assert row['scraper'] == 'Q1227164_fust.py'
    assert row['num_features'] == 3
    assert row['error_log'] == 'log\nwith multiple lines and "quotes"'
