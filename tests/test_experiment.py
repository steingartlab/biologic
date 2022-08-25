import pytest
from threading import Event, Thread
from time import sleep

from biologic.experiment import Experiment, run
from biologic.potentiostats import HCP1005
from tests.params import cp_params


@pytest.fixture
def experiment_():
    experiment_ = Experiment()

    return experiment_


def test_initial_status(experiment_: Experiment):
    assert experiment_.status == 'stopped'


def test_check_status_stopped(experiment_: Experiment):
    experiment_.check_status(state=0)

    assert experiment_.status == 'stopped'


def test_check_status_paused(experiment_: Experiment):
    experiment_.check_status(state=2)

    assert experiment_.status == 'paused'


def test_check_status_running(experiment_: Experiment):
    experiment_.check_status(state=1)

    assert experiment_.status == 'running'


@pytest.fixture
def potentiostat_():
    potentiostat_ = HCP1005()

    return potentiostat_


@pytest.fixture
def pill():
    pill = Event()

    return pill


def test_run(potentiostat_: HCP1005, pill: Event, experiment_: Experiment):
    """Very minimalistic. More nuanced tests in test_app.py"""

    run(
        potentiostat=potentiostat_,
        raw_params=cp_params,
        pill=pill,
        experiment_=experiment_
    )

    pill.set()

def test_setting_pill(potentiostat_: HCP1005, pill: Event, experiment_: Experiment):
    thread = Thread(target=run, args=(potentiostat_, cp_params, pill, experiment_))
    thread.start()
    sleep(1)
    pill.set()