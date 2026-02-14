import pytest
from src.main import app as flask_app
from src.models import db as _db

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # A temporary DB in the computer's memory
    })
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()