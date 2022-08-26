import tempfile


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({"TESTING": True,
                     "DATABASE": db_path,
                      })
