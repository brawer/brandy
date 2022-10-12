# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(test_config=None):
    # Create and configure the app.
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'brandy.sqlite'),
    )

    # Load the configuration file, if it exists.
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Configure the Jinja2 template engine to emit compact html.
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.keep_trailing_newline = True

    # Set up database connection and register Flask blueprints.
    from . import db, collections, scrapes, tiles, users
    db.init_app(app)
    app.register_blueprint(collections.bp)
    app.register_blueprint(scrapes.bp)
    app.register_blueprint(tiles.bp)
    app.register_blueprint(users.bp)

    # Tell Flask it is behind a proxy.
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    return app
