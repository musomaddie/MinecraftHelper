import os
import tempfile

import pytest

from block_adder_flask import create_app
from block_adder_flask.db_for_flask import get_db, reset_entire_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {"TESTING": True,
         "DATABASE": db_path,
         })

    with app.app_context():
        reset_entire_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)
