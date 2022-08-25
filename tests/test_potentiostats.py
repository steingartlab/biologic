"""Requires the PC to be physically connected via ethernet to an
HCP-1005 potentiostat in order for this testing module to pass. 
"""

import json
import pytest

from biologic import utils
from biologic.potentiostats import InstrumentFinder, HCP1005, Config
from biologic.structures import EccParams
from biologic.techniques import set_technique_params
from tests.params import cp_params

############################################################################
'''Boilerplate'''

with open('biologic\\config.json') as f:
    config = json.load(f)

type_ = 'KBIO_DEV_HCP1005'
usb_port = 'USB0'
channels = [1]

DRIVERPATH = 'drivers\\'

############################################################################
'''Fixtures'''


@pytest.fixture
def finding_instance():
    instance_ = InstrumentFinder()

    return instance_


@pytest.fixture
def finder():
    finder = InstrumentFinder()
    finder.find()

    return finder


@pytest.fixture
def pstat_instance():
    pstat_instance = HCP1005()

    return pstat_instance


@pytest.fixture
def connection(pstat_instance: HCP1005):
    pstat_instance.connect(usb_port=usb_port)

    yield pstat_instance

    # Teardown
    pstat_instance.disconnect()


@pytest.fixture
def technique() -> list[EccParams]:
    parsed_params, _, _ = utils.parse_raw_params(raw_params=cp_params)
    c_technique_params = set_technique_params(parsed_params)

    return c_technique_params


@pytest.fixture
def technique_paths() -> list[str]:
    _, technique_paths, _ = utils.parse_raw_params(raw_params=cp_params)

    return technique_paths



@pytest.fixture
def loaded_technique(connection: HCP1005, technique: list[EccParams], technique_paths: list[str]):
    connection.stop_channel()
    connection.load_technique(
        technique_paths=technique_paths, c_tecc_params=technique
        )

    return connection


@pytest.fixture
def started_channel(loaded_technique: HCP1005):
    loaded_technique.start_channel()

    yield loaded_technique

    loaded_technique.stop_channel()


@pytest.fixture
def config():
    config = Config(type=type_)

    config.connect(usb_port=usb_port)

    return config


############################################################################
'''Unit tests'''


def test_successful_finding(finding_instance: InstrumentFinder):
    finding_instance.find()

    assert isinstance(finding_instance.instrument_type, str)
    assert isinstance(finding_instance.usb_port, str)

    # usb_port = ipaddress.usb_port(finding_instance.usb_port)

    # assert isinstance(usb_port, ipaddress.IPv4Address)


def test_get_error_status(config: Config):
    config.get_error_status()


def test_get_message(config: Config):
    message = config.get_message()

    assert isinstance(message, str)


def test_test_connection(config: Config):
    config.test_connection()


def test_test_communication_speed(config: Config):
    config.test_communication_speed()


def test_load_firmware(config: Config):
    c_results = config.load_firmware(channels=channels)

    assert sum(c_results) == 0


def test_get_channels_plugged(config: Config):
    channels_plugged = config.get_channels_plugged()

    assert channels_plugged == [True]


def test_is_channel_plugged(config: Config):
    is_plugged = config.is_channel_plugged()

    assert is_plugged is True


def test_get_channel_info(config: Config):
    channel_info = config.get_channel_info()

    assert isinstance(channel_info, dict)


################################################


def test_get_current_values_wo_starting(connection: HCP1005):
    connection.stop_channel()
    current_values = connection.get_current_values()

    assert current_values['State'] == 0


def test_connect(pstat_instance: HCP1005, finder: InstrumentFinder):

    assert finder.usb_port == 'USB0'
    pstat_instance.connect(usb_port=finder.usb_port)


def test_load_technique(
    connection: HCP1005, technique: list[EccParams], technique_paths: list[str]
    ):
    connection.load_technique(
        technique_paths=technique_paths, c_tecc_params=technique
        )


def test_start_channel(loaded_technique: HCP1005):
    loaded_technique.start_channel()


def test_get_current_values(started_channel: HCP1005):
    current_values = started_channel.get_current_values()

    assert isinstance(current_values, dict)


def test_stop_channel(started_channel: HCP1005):
    started_channel.stop_channel()


# def test_get_data(started_channel: potentiostats.HCP1005):
#     something = started_channel.get_data()


def test_disconnect(connection: HCP1005):
    connection.disconnect()
