# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Flask blueprint for handling /tiles/*

import flask
import json
import subprocess
import zlib

from brandy.db import get_db, build_find_features_query
from brandy.geometry import tile_to_wgs84

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
    fuzz = 6  # how many pixels we allow to be off, for incaccurate clicks
    p = tile_to_wgs84(zoom + 8, x * 256 + i, y * 256 + j)
    p1 = tile_to_wgs84(zoom + 8, x * 256 + i - fuzz, y * 256 + j - fuzz)
    p2 = tile_to_wgs84(zoom + 8, x * 256 + i + fuzz, y * 256 + j + fuzz)
    bbox = (p1[0], p2[1], p2[0], p1[1])
    query, params = build_find_features_query(brand_id, bbox=bbox, limit=1)
    features = []
    f = get_db().execute(query, params).fetchone()
    if f != None:
        features.append({
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [f['lng'], f['lat']]},
            'id': f['feature_id'],
            'properties': json.loads(zlib.decompress(f['props']))
        })
        print(features)
    resp = flask.json.jsonify({
        'type': 'FeatureCollection',
        'features': features
    })
    resp.headers['Content-Type'] = 'application/geo+json'
    return resp
