# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Flask blueprint for handling /collections/*
#
# We implement the OGC WFS 3.0 API, see https://ogcapi.ogc.org/features/.


from datetime import datetime
import hashlib
from http import HTTPStatus
import json
import struct
import time
import zlib

import flask
from flask_accept import accept, accept_fallback
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

import brandy.auth, brandy.geometry
from brandy.auth import auth
from brandy.db import get_db

bp = flask.Blueprint('collections', __name__, url_prefix='/collections')


@bp.route('')
@accept_fallback
def index():
    return index_json()


@bp.route('.json')
@index.support('application/json')
def index_json():
    db = get_db()
    last_modified = None
    collections = []
    for brand in db.execute(
        'SELECT wikidata_id, last_modified, min_lng, min_lat, max_lng, max_lat'
        ' FROM brand').fetchall():
            brand_id = brand['wikidata_id']
            if last_modified == None or last_modified < brand['last_modified']:
                last_modified = brand['last_modified']
            bbox = [
                brand['min_lng'], brand['min_lat'],
                brand['max_lng'], brand['max_lat']
            ]
            collections.append(_format_brand_collection_json(brand_id, bbox))
    resp = flask.json.jsonify({'links': [], 'collections': collections})
    resp.headers['Content-Type'] = 'application/json'
    if last_modified != None:
        resp.headers['Last-Modified'] = last_modified.isoformat() + 'Z'
    if not flask.request.path.endswith('.json'):
        resp.headers['Vary'] = 'Accept'
    return resp


@bp.route('/Q<int:brand_id>-brand')
@accept_fallback
def collection(brand_id):
    return collection_json(brand_id)


@bp.route('/Q<int:brand_id>-brand.json')
@collection.support('application/json')
def collection_json(brand_id):
    db = get_db()
    brand = db.execute(
        'SELECT min_lng, min_lat, max_lng, max_lat'
        ' FROM brand WHERE wikidata_id = ?',
        (brand_id,)).fetchone()
    if brand == None:
        raise NotFound()
    bbox = [
        brand['min_lng'], brand['min_lat'],
        brand['max_lng'], brand['max_lat']
    ]
    resp = flask.json.jsonify(_format_brand_collection_json(brand_id, bbox))
    if not flask.request.path.endswith('.json'):
        resp.headers['Vary'] = 'Accept'
    return resp


@bp.route('/Q<int:brand_id>-brand.html')
@collection.support('text/html')
def collection_html(brand_id):
    db = get_db()
    brand = db.execute(
        'SELECT last_checked, last_modified,'
        '  min_lng, min_lat, max_lng, max_lat'
        '  FROM brand WHERE wikidata_id = ?',
        (brand_id,)).fetchone()
    if brand == None:
        raise NotFound()
    data = {
        'bbox': [
            brand['min_lng'], brand['min_lat'],
            brand['max_lng'], brand['max_lat']
        ],
        'brand_id': 'Q%d' % brand_id,
        'brand_name': 'Brand',
        'last_checked': brand['last_checked'].isoformat() + 'Z',
        'last_modified': brand['last_modified'].isoformat() + 'Z',
        'items_url': flask.url_for('collections.items', _external=True,
                                   brand_id=brand_id)
    }
    rendered = flask.render_template(
        'collections/map.html', data=data, data_json=json.dumps(data))
    resp = flask.make_response(rendered)
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

    brand = db.execute(
        'SELECT last_modified FROM brand WHERE wikidata_id = ?',
        (brand_id,)).fetchone()
    if brand == None:
        raise NotFound()
    last_modified = brand['last_modified']
    return generate_brand_items_json(db, brand_id), {
        'Content-Type': 'application/geo+json',
        'Last-Modified': last_modified.isoformat() + 'Z',
    }


@flask.stream_with_context
def generate_brand_items_json(db, brand_id):
    yield '{"type":"FeatureCollection","features":['
    first = True
    for f in db.execute(
        'SELECT feature_id, lng, lat, props'
        ' FROM brand_feature WHERE brand_id = ?',
        (brand_id,)
    ).fetchall():
        feature = {
            'type': 'Feature',
            'id': f['feature_id'],
            'geometry': {
                'type': 'Point',
                'coordinates': [f['lng'], f['lat']]
            },
            'properties': json.loads(zlib.decompress(f['props']))
        }
        sep = '\n' if first else ',\n'
        first = False
        yield '%s%s' % (sep, json.dumps(feature))
    yield ']}\n'


def store_scraped(db, brand_id, scraped):
    now = datetime.now()
    content = json.load(scraped)  # TODO: Use json_stream.
    bbox = brandy.geometry.bbox(content)
    if bbox == None:
        raise BadRequest()
    bbox = [float(c) for c in bbox]
    cursor = db.cursor()

    old = {}
    for f in cursor.execute(
        'SELECT feature_id, hash_hi, hash_lo, last_modified'
        ' FROM brand_feature WHERE brand_id = ?',
        (brand_id,)
    ).fetchall():
        old[f['feature_id']] = (f['hash_hi'], f['hash_lo'], f['last_modified'])
    last_modified = None

    cursor.execute('DELETE FROM brand WHERE wikidata_id = ?', (brand_id,))
    cursor.execute('DELETE FROM brand_feature WHERE brand_id = ?', (brand_id,))
    cursor.execute('DELETE FROM brand_feature_rtree WHERE brand_id = ?',
                   (brand_id,))

    for feature in content['features']:
        min_lng, min_lat, max_lng, max_lat = brandy.geometry.bbox(feature)
        lng, lat = (min_lng + max_lng) / 2, (min_lat + max_lat) / 2
        props = feature.get('properties', {})
        feature_id = str(feature.get('id') or props['ref'])
        props_json = json.dumps(props, ensure_ascii=False,
                                separators=(',', ':'), sort_keys=True)
        props_compressed = zlib.compress(props_json.encode('utf-8'), level=9)
        hash_hi, hash_lo = hash_blob('%s%f%f%s' % (id, lng, lat, props_json))
        feature_last_modified = now
        if feature_id in old:
            old_hash_hi, old_hash_lo, old_last_modified = old[feature_id]
            if hash_hi == old_hash_hi and hash_lo == old_hash_lo:
                feature_last_modified = old_last_modified
        if last_modified == None or last_modified < feature_last_modified:
            last_modified = feature_last_modified
        cursor.execute(
            'INSERT INTO brand_feature ('
            '    brand_id, feature_id, lng, lat,'
            '    hash_hi, hash_lo, last_modified, props)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (brand_id, feature_id, lng, lat, hash_hi, hash_lo, last_modified,
             props_compressed))
        internal_id = cursor.lastrowid
        cursor.execute(
            'INSERT INTO brand_feature_rtree ('
            '    internal_id, min_lng, max_lng, min_lat, max_lat, brand_id)'
			'VALUES (?, ?, ?, ?, ?, ?)',
			(internal_id, min_lng, max_lng, min_lat, max_lat, brand_id))

    last_checked = now
    if last_modified == None:
        last_modified = now
    db.execute(
        'INSERT INTO brand ('
        '    wikidata_id, last_checked, last_modified,'
        '    min_lng, min_lat, max_lng, max_lat)'
       'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (brand_id, last_checked, last_modified,
         bbox[0], bbox[1], bbox[2], bbox[3]))


def hash_blob(b):
    # MurmurHash3 would probably be the better algorithm, but it is not
    # packaged yet in Alpine Linux (which we run in production). We could
    # set up a C compiler in our build, but that seems like overkill.
    if type(b) == str: b = b.encode('utf-8')
    return struct.unpack('>ll', hashlib.shake_128(b).digest(8))


def _format_brand_collection_json(brand_id, bbox):
    self_url = flask.url_for('collections.collection', _external=True,
                             brand_id=brand_id)
    items_url = flask.url_for('collections.items', _external=True,
                              brand_id=brand_id)
    return {
        'id': 'Q%s-brand' % brand_id,
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
    }
