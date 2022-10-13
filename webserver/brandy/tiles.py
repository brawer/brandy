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
    layer = {
        'marker-fill': '#4287F5',
        'marker-width': 6.0
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

