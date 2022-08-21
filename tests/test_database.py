import pytest

from biologic import config, database

path = 'brix2/test/test'
full_path = f'{config.drops_prefix}/{path}/'
data = {'column': [0, 1, 2]}


@pytest.fixture
def db_instance():
    instance = database.Database(path=path)

    return instance


def test_url(db_instance):
    assert db_instance.url == full_path


def test_write(db_instance):
    status = db_instance.write(payload=data, table='test')

    assert status.is_published
