import flask
import os
import pytest

from app import configure_routes

@pytest.fixture
def client():
    app = flask.Flask(__name__)
    configure_routes(app)
    client = app.test_client()

    return client

def test_base_route(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.get_data() == b'Flask BioLogic server running'


def test_random_route_failure(client):
    response = client.get('/some_nonexistent_url')
    assert response.status_code == 404


def test_logs():
    assert os.path.isfile('logs/logs.log')