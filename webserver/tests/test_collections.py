# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Tests on url path /collections/*


import base64
import io
from http import HTTPStatus
import json

import pytest

import brandy.collections
from brandy.db import create_user, get_db

# TODO: Copied from test_users.py. Move into test utilities.
def basic_auth_header(username, password):
    cred = '%s:%s' % (username, password)
    cred = base64.b64encode(cred.encode('utf-8')).decode('utf-8')
    return {'Authorization': 'Basic %s' % cred}


@pytest.fixture
def users(app):
    p = {'testbot': 'secret'}
    with app.app_context():
        for username, password in p.items():
            create_user(username, password)
        get_db().commit()
    return p


@pytest.fixture
def basic_auth(users):
    return lambda u: basic_auth_header(u, users.get(u, ''))


# Uploaded by fake scraper.
Q72_scraped = {
    'type': 'FeatureCollection',
    'features': [{
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [8.5, 47.6]},
        'properties': {'brand:wikidata': 'Q72'}
    }, {
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [8.6, 47.3]},
        'properties': {'brand:wikidata': 'Q72'}
    }]
}


Q72_collection = {
    'id': 'Q72',
    'extent': {
        'spatial': {'bbox': [[8.5, 47.3, 8.6, 47.6]]},
    },
    'links': [{
        'rel': 'self',
        'href': 'https://brandy.test/t/collections/Q72-brand.json',
        'type': 'application/json'
    }, {
        'rel': 'alternate',
        'href': 'https://brandy.test/t/collections/Q72-brand.html',
        'type': 'text/html'
    }, {
        'rel': 'items',
        'href': 'https://brandy.test/t/collections/Q72-brand/items'
    }]
}


@pytest.fixture
def q72(basic_auth, client):
    scraped = io.BytesIO(json.dumps(Q72_scraped).encode('utf-8'))
    r = client.post(
        '/collections/Q72-brand/items', headers=basic_auth('testbot'),
        data = {'scraped': (scraped, 's.json', 'application/geo+json')})
    assert r.status_code == HTTPStatus.CREATED


class TestGetCollection:
    def test_json(self, q72, client):
        r = client.get('/collections/Q72-brand.json')
        assert r.status_code == HTTPStatus.OK
        assert r.headers['Content-Type'] == 'application/json'
        assert r.headers.get('Vary') == None
        assert r.json == Q72_collection

    def test_html(self, q72, client):
        r = client.get('/collections/Q72-brand.html')
        assert r.status_code == HTTPStatus.OK
        assert r.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert r.headers.get('Vary') == None

    def test_accept_json(self, q72, client):
        r = client.get('/collections/Q72-brand',
                       headers={'Accept': 'application/json'})
        assert r.status_code == HTTPStatus.OK
        assert r.headers['Content-Type'] == 'application/json'
        assert r.headers['Vary'] == 'Accept'
        assert r.json == Q72_collection

    def test_accept_html(self, q72, client):
        r = client.get('/collections/Q72-brand',
                       headers={'Accept': 'text/html'})
        assert r.status_code == HTTPStatus.OK
        assert r.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert r.headers['Vary'] == 'Accept'

    def test_accept_default(self, q72, client):
        r = client.get('/collections/Q72-brand')
        assert r.status_code == HTTPStatus.OK
        assert r.headers['Content-Type'] == 'application/json'
        assert r.headers['Vary'] == 'Accept'
        assert r.json == Q72_collection

    def test_accept_fallback(self, q72, client):
        r = client.get('/collections/Q72-brand',
                       headers={'Accept': 'image/png'})
        assert r.status_code == HTTPStatus.OK
        assert r.headers['Content-Type'] == 'application/json'
        assert r.headers['Vary'] == 'Accept'
        assert r.json == Q72_collection

    def test_not_found(self, client):
        r = client.get('/collections/Q404-brand')
        assert r.status_code == HTTPStatus.NOT_FOUND

    def test_json_not_found(self, client):
        r = client.get('/collections/Q404-brand.json')
        assert r.status_code == HTTPStatus.NOT_FOUND

    def test_html_not_found(self, client):
        r = client.get('/collections/Q404-brand.html')
        assert r.status_code == HTTPStatus.NOT_FOUND


class TestPostItems:
    def test(self, basic_auth, client):
        scraped = io.BytesIO(json.dumps(Q72_scraped).encode('utf-8'))
        r = client.post(
            '/collections/Q72-brand/items', headers=basic_auth('testbot'),
            data = {'scraped': (scraped, 'file.json', 'application/geo+json')})
        assert (r.text, r.status_code) == ('Created', HTTPStatus.CREATED)
        assert r.headers['Location'] == \
            'https://brandy.test/t/collections/Q72-brand/items'
        r = client.get('/collections/Q72-brand',
                       headers={'Accept': 'application/json'})
        assert r.status_code == HTTPStatus.OK
        assert r.json == Q72_collection

    def test_unauthorized(self, client):
        r = client.post('/collections/Q72-brand/items', data={'scraped': '{}'})
        assert r.status_code == HTTPStatus.UNAUTHORIZED
        assert r.headers['WWW-Authenticate'].startswith('Basic')
