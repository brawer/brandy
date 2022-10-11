# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Flask blueprint for handling /collections/*
#
# We implement the OGC WFS 3.0 API, see https://ogcapi.ogc.org/features/.


import flask
from flask_accept import accept, accept_fallback
from http import HTTPStatus
import json
import time
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

import brandy.auth, brandy.geometry
from brandy.auth import auth
from brandy.db import get_db

bp = flask.Blueprint('collections', __name__, url_prefix='/collections')


@bp.route('/Q<int:brand_id>-brand')
@accept_fallback
def collection(brand_id):
    return collection_json(brand_id)


@bp.route('/Q<int:brand_id>-brand.json')
@collection.support('application/json')
def collection_json(brand_id):
    db = get_db()
    brand = db.execute(
        'SELECT scraped, min_lng_e7, min_lat_e7, max_lng_e7, max_lat_e7'
        ' FROM brand WHERE wikidata_id = ?',
        (brand_id,)).fetchone()
    if brand == None:
        raise NotFound()
    bbox = [
        round(float(brand['min_lng_e7']) * 1e-7, 7),
        round(float(brand['min_lat_e7']) * 1e-7, 7),
        round(float(brand['max_lng_e7']) * 1e-7, 7),
        round(float(brand['max_lat_e7']) * 1e-7, 7)
    ]
    scraped = brand['scraped'].strftime('%Y-%m-%dT%H:%M:%SZ')
    self_url = flask.url_for('collections.collection', _external=True,
                             brand_id=brand_id)
    items_url = flask.url_for('collections.items', _external=True,
                              brand_id=brand_id)
    resp = flask.json.jsonify({
        'id': 'Q%s' % brand_id,
        'extent': {
            'spatial': {'bbox': [bbox]},
        },
        'links': [
            {
                'rel': 'self',
                'href': self_url + '.json',
                'type': 'application/json'
			},
            {
                'rel': 'alternate',
                'href': self_url + '.html',
                'type': 'text/html'
			},
            {'rel': 'items', 'href': items_url}
        ]
    })
    if not flask.request.path.endswith('.json'):
        resp.headers['Vary'] = 'Accept'
    return resp


@bp.route('/Q<int:brand_id>-brand.html')
@collection.support('text/html')
def collection_html(brand_id):
    _ = collection_json(brand_id)  # raises NotFound for unknown brands
    resp = flask.Response(
        '<html><body>TODO: Web page for Q%s</body></html>' % brand_id)
    if not flask.request.path.endswith('.html'):
        resp.headers['Vary'] = 'Accept'
    return resp


@bp.route('/Q<int:brand_id>-brand/items', methods=('GET', 'POST'))
@auth.login_required(optional=True)
def items(brand_id):
    urlpath = flask.url_for('collections.items', _external=True,
                            brand_id=brand_id)
    db = get_db()
    if flask.request.method == 'POST':
        user = auth.current_user()
        if user == None:
            r = flask.Response(status=HTTPStatus.UNAUTHORIZED)
            r.headers['WWW-Authenticate'] = auth.authenticate_header()
            return r
        logfile = flask.request.files.get('log')
        # TODO: Store log.
        scraped = flask.request.files.get('scraped')
        if scraped != None:
            store_scraped(db, brand_id, scraped)
        resp = flask.Response('Created', HTTPStatus.CREATED)
        resp.headers['Location'] = urlpath
        db.commit()
        return resp

    return '''
    <!doctype html>
    <title>Upload</title>
    <h1>Upload</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=scraped>
      <input type=file name=log>
      <input type=submit value=Upload>
    </form>
    ''', 404
    raise NotFound()


def store_scraped(db, brand_id, scraped):
    content = json.load(scraped)  # TODO: Use json_stream.
    bbox = brandy.geometry.bbox(content)
    if bbox == None:
        raise BadRequest()
    bbox_e7 = [int(c * 1e7) for c in bbox]
    db.execute('DELETE FROM brand WHERE wikidata_id = ?', (brand_id,))
    db.execute(
        'INSERT INTO brand ('
        '    wikidata_id, '
        '    min_lng_e7, min_lat_e7, max_lng_e7, max_lat_e7)'
        'VALUES (?, ?, ?, ?, ?)',
        (brand_id, bbox_e7[0], bbox_e7[1], bbox_e7[2], bbox_e7[3]))
