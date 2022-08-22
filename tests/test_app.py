import flask
from flask.testing import FlaskClient
import os
import pytest
from time import sleep

from app import configure_routes

from tests.params import raw_params


@pytest.fixture
def client():
    app = flask.Flask(__name__)
    configure_routes(app)
    client = app.test_client()

    return client


def test_base_route(client: FlaskClient):
    response = client.get('/')

    assert response.status_code == 200
    assert response.get_data() == b'Flask BioLogic server running'


def test_random_route_failure(client: FlaskClient):
    response = client.get('/some_nonexistent_url')
    assert response.status_code == 404


def test_logs():
    assert os.path.isfile('logs/logs.log')


def test_check_status_not_started(client: FlaskClient):
    response = client.get('/check_status')

    assert response.status_code == 200
    assert response.get_data() == b'No experiment instance in scope'


def test_basic_run(client: FlaskClient):
    response = client.post('/run', json=raw_params)

    assert response.status_code == 200
    assert response.get_data() == b'Technique started'


@pytest.fixture
def running_client(client: FlaskClient):
    client.post('/run', json=raw_params)
    
    # Otherwise it doesn't have time to initiate a pstat 
    # connection and change status to running
    sleep(2)

    return client


def test_check_status_running(running_client: FlaskClient):

    response = running_client.get('/check_status')

    assert response.status_code == 200
    assert response.get_data() == b'running'


def test_stop(running_client: FlaskClient):
    response = running_client.get('/stop')

    assert response.status_code == 200
    assert response.get_data() == b'Technique stopped'


def test_block_new_if_already_running(running_client: FlaskClient):
    response = running_client.post('/run')

    assert response.status_code == 200
    assert response.get_data() == b'Aborted: Experiment already running'