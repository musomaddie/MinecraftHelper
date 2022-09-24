import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="top secret shhhhhh",
        DATABASE=os.path.join(app.instance_path, "minecraft_items.db")
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db_for_flask
    db_for_flask.init_app(app)

    from . import manual_population
    app.register_blueprint(manual_population.bp)

    from . import get_group_info
    app.register_blueprint(get_group_info.bp, url_prefix="/preexisting_group")

    return app
