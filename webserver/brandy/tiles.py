# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Flask blueprint for handling /tiles/*

import flask
import subprocess

from brandy.db import get_db

bp = flask.Blueprint('tiles', __name__, url_prefix='/tiles')

@bp.route('/Q<int:brand_id>-brand/<int:zoom>/<int:x>/<int:y>.png')
def tile(brand_id, x, y, zoom):
    db = get_db()
    with subprocess.Popen(
        'rendertile', stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
        for f in db.execute(
            'SELECT feature_id, lng, lat'
            ' FROM brand_feature WHERE brand_id = ?',
            (brand_id,)
        ).fetchall():
           proc.stdin.write(b'%g,%g\n' % (f['lng'], f['lat']))
        png, _err = proc.communicate(timeout=5)
    return flask.Response(response=png, headers={
        'Content-Type': 'image/png'
    })

