# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Flask blueprint for handling /scrapes/*

import flask
import json

from brandy.db import get_db

bp = flask.Blueprint('scrapes', __name__, url_prefix='/scrapes')

@bp.route('/')
def index():
    db = get_db()
    scrapes = db.execute(
        'SELECT scrape.id AS id, scraped, scraper.name AS scraper_name '
		' FROM scrape'
        ' INNER JOIN scraper ON scrape.scraper_id = scraper.id'
        ' ORDER BY scraped DESC'
        ' LIMIT 50'
    ).fetchall()
    return flask.render_template('scrapes/index.html', scrapes=scrapes)


@bp.route('/<int:id>/')
def scrape(id):
    db = get_db()
    scrape = db.execute(
        'SELECT scrape.id AS id, scraped, scraper.name AS scraper_name, num_features, error_log'
		' FROM scrape '
        ' INNER JOIN scraper ON scrape.scraper_id = scraper.id'
        ' WHERE scrape.id = ?',
        (id,)
    ).fetchone()
    if not scrape:
        flask.abort(404)
    return flask.render_template('scrapes/scrape.html', scrape=scrape)


@bp.route('/upload', methods=('GET', 'POST'))
def upload():
    # TODO: Authenticate.
    if flask.request.method == 'POST':
        scraper_name = flask.request.form['scraper']
        data = flask.request.form['data']
        data = json.loads(data) if data else {}
        num_features = len(data['features'])
        error_log = flask.request.form['error_log']
        db = get_db()
        cursor = db.cursor()
        res = cursor.execute(
		    'SELECT id FROM scraper WHERE name = ?',
			(scraper_name,)).fetchone()
        scraper_id = res[0] if res else None
        if not scraper_id:
            cursor.execute(
                'INSERT OR IGNORE INTO scraper (name)'
                ' VALUES (?)',
                (scraper_name,))
            scraper_id = cursor.lastrowid
        cursor.execute(
            'INSERT INTO scrape (scraper_id, num_features, error_log)'
            ' VALUES (?, ?, ?)',
            (scraper_id, num_features, error_log)
        )
        id = cursor.lastrowid
        db.commit()
        loc = flask.url_for('scrapes.scrape', id=id)
        html = flask.render_template('scrapes/upload_created.html',
                                     scrape={'id': id}, location=loc)
        r = flask.Response(html, status=201)
        r.headers['Location'] = loc
        return r

    return flask.render_template('scrapes/upload.html')
