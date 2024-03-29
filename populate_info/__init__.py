import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="top secret shhhhhh",
    )
    toolbar = DebugToolbarExtension(app)
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from populate_info.population_pages import item_blueprint
    app.register_blueprint(item_blueprint)

    return app
