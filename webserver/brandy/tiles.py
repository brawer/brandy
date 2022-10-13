# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Flask blueprint for handling /tiles/*

import flask
import json
import subprocess

from brandy.db import get_db

bp = flask.Blueprint('tiles', __name__, url_prefix='/tiles')

@bp.route('/Q<int:brand_id>-brand/<int:zoom>/<int:x>/<int:y>.png')
def tile(brand_id, zoom, x, y):
    tile = {'zoom': zoom, 'x': x, 'y': y}
    if zoom <= 3:
        marker_width = 5.0
    if zoom <= 6:
        marker_width = 6.0
    elif zoom >= 10:
        marker_width = 16.0
    else:
        marker_width = {7: 9.0, 8: 12.5, 9: 14.0}[zoom]
    layer = {
        'marker-fill': '#4287F5',
        'marker-width': marker_width
    }
    db = get_db()
    with subprocess.Popen(
        'rendertile', stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
        proc.stdin.write(('T %s\n' % json.dumps(tile)).encode('utf-8'))
        proc.stdin.write(('L %s\n' % json.dumps(layer)).encode('utf-8'))
        for f in db.execute(
            'SELECT feature_id, lng, lat'
            ' FROM brand_feature WHERE brand_id = ?',
            (brand_id,)
        ).fetchall():
           proc.stdin.write(b'P [%g,%g]\n' % (f['lng'], f['lat']))
        png, _err = proc.communicate(timeout=5)
    return flask.Response(response=png, headers={
        'Content-Type': 'image/png'
    })


@bp.route('/Q<int:brand_id>-brand/<int:zoom>/<int:x>/<int:y>/<int:i>/<int:j>.geojson')
def clicked_feature(brand_id, zoom, x, y, i, j):  # OGC WMTS GetFeatureInfo
    resp = flask.json.jsonify({
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [12.345, 5.678]},
            'id': 'TODO-id',
            'properties': {
                'addr:city': 'Bern',
                'addr:street': 'Länggassstrasse',
                'addr:housenumber': '27',
                'addr:postcode': '3012',
                'brand:wikidata': 'Q%d' % brand_id,
                'name': 'TODO'
            }
        }]
    })
    resp.headers['Content-Type'] = 'application/geo+json'
    return resp
