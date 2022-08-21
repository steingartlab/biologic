import pytest
from threading import Event
import time

from biologic import experiment, potentiostats
from tests.params import raw_params

@pytest.fixture
def experiment_():
    experiment_ = experiment.Experiment()

    return experiment_


def test_initial_status(experiment_: experiment.Experiment):
    assert experiment_.status == 'running'


def test_check_status_stopped(experiment_: experiment.Experiment):
    experiment_.check_status(state=0)

    assert experiment_.status == 'stopped'


def test_check_status_paused(experiment_: experiment.Experiment):
    experiment_.check_status(state=2)

    assert experiment_.status == 'paused'


@pytest.fixture
def potentiostat_():
    potentiostat_ = potentiostats.HCP1005()

    return potentiostat_


@pytest.fixture
def pill():
    pill = Event()

    return pill


def test_run(potentiostat_: potentiostats.Potentiostat, pill: Event):
    """Very minimalistic. More nuanced tests in test_app.py"""
    
    experiment.run(
        potentiostat=potentiostat_, raw_params=raw_params, pill=pill
        )
