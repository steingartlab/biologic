"""The HCP-1005 only contains a single channel, which simplifies testing a bit.
Would have to be expanded slightly if this library were to be generalized.
"""

import ipaddress
import json
import pytest

from biologic import potentiostats, structures, techniques

with open('biologic/config.json') as f:
    settings = json.load(f)

driverpath = settings['driver']['driverpath']
driver_example = settings['driver']['example_driver']

channels = [1]
label = 'Rest_time_T'
bool_ = True
single = 10.0
int_ = 2
index = 0
int_representing_a_float = 100

technique_params = {
    'duration': techniques.ECC_param("Rest_time_T", float),
    'record_dt': techniques.ECC_param("Record_every_dT", float),
    'E_range': techniques.ECC_param("E_Range", int),
    }
technique_path = driverpath + 'ocv.ecc'


# @pytest.fixture
# def tecc_param():
#     tecc_param = structures.TEccParam()

#     return tecc_param


# def test_define_bool_param(tecc_param):
#     potentiostats.define_bool_param(
#         label=label, value=bool_, index=index, tecc_param=tecc_param
#         )


# def test_define_single_param(tecc_param):
#     potentiostats.define_single_param(
#         label=label, value=single, index=index, tecc_param=tecc_param
#         )


# def test_define_integer_param(tecc_param):
#     potentiostats.define_integer_param(
#         label=label, value=int_, index=index, tecc_param=tecc_param
#         )


def test_convert_numeric_to_single():
    potentiostats.convert_numeric_to_single(
        numeric=int_representing_a_float
        )


@pytest.fixture
def finding_instance():
    instance_ = potentiostats.InstrumentFinder()

    return instance_


def test_successful_finding(
    finding_instance: potentiostats.InstrumentFinder
    ):
    finding_instance.find()

    assert isinstance(finding_instance.ip_address, str)

    ip_address = ipaddress.ip_address(finding_instance.ip_address)

    assert isinstance(ip_address, ipaddress.IPv4Address)


# ####################################################


@pytest.fixture
def finder():
    finder = potentiostats.InstrumentFinder()
    finder.find()

    return finder


@pytest.fixture
def potentiostat_instance(finder: potentiostats.InstrumentFinder):
    # if finder.instrument_type == 'HCP-1005':
    #     potentiostat_instance = potentiostats.HCP1005()
    # elif finder.instrument_type == 'SP-150':
    #     potentiostat_instance = potentiostats.SP150()
    # else:
    #     raise ValueError(
    #         f'Instrument type not defined {finder.instrument_type}.'
    #         )
    potentiostat_instance = potentiostats.HCP1005()

    return potentiostat_instance


def test_connect(
    potentiostat_instance: potentiostats.GeneralPotentiostat,
    finder: potentiostats.InstrumentFinder
    ):
    # pass
    potentiostat_instance.connect(ip_address=finder.ip_address)


@pytest.fixture
def connection(
    potentiostat_instance: potentiostats.GeneralPotentiostat,
    finder: potentiostats.InstrumentFinder
    ):
    potentiostat_instance.connect(ip_address=finder.ip_address)

    yield potentiostat_instance

    # Teardown
    potentiostat_instance.disconnect()


def test_test_connection(
    connection: potentiostats.GeneralPotentiostat
    ):
    connection.test_connection()


def test_test_communication_speed(
    connection: potentiostats.GeneralPotentiostat
    ):
    connection.test_communication_speed()


def test_disconnect(connection: potentiostats.GeneralPotentiostat):
    connection.disconnect()


def test_load_firmware(connection: potentiostats.GeneralPotentiostat):
    c_results = connection.load_firmware(channels=channels)

    assert sum(c_results) == 0


def test_get_channels_plugged(
    connection: potentiostats.GeneralPotentiostat
    ):
    channels_plugged = connection.get_channels_plugged()

    assert channels_plugged == [True]


def test_is_channel_plugged(
    connection: potentiostats.GeneralPotentiostat
    ):
    is_plugged = connection.is_channel_plugged()

    assert is_plugged is True


def test_get_channel_info(
    connection: potentiostats.GeneralPotentiostat
    ):
    channel_info = connection.get_channel_info()

    assert isinstance(channel_info, dict)


def test_get_message(connection: potentiostats.GeneralPotentiostat):
    message = connection.get_message()

    assert isinstance(message, str)


def test_get_error_status(
    connection: potentiostats.GeneralPotentiostat
    ):
    connection.get_error_status()


@pytest.fixture
def technique():
    c_technique_params = techniques.parse_technique_params(technique_params=technique_params)

    return c_technique_params


def test_load_technique(
    connection: potentiostats.GeneralPotentiostat,
    technique: structures.EccParams
    ):
    connection.load_technique(
        technique_path=technique_path, c_tecc_params=technique
        )


@pytest.fixture
def loaded_technique(
    connection: potentiostats.GeneralPotentiostat,
    technique: structures.EccParams
    ):
    connection.load_technique(
        technique_path = technique_path,
        c_tecc_params=technique)

    return connection


def test_start_channel(
    loaded_technique: potentiostats.GeneralPotentiostat
    ):
    loaded_technique.start_channel()


@pytest.fixture
def started_channel(
    loaded_technique: potentiostats.GeneralPotentiostat
    ):
    loaded_technique.start_channel()

    yield loaded_technique

    loaded_technique.stop_channel()


def test_get_current_values(
    started_channel: potentiostats.GeneralPotentiostat
    ):
    current_values = started_channel.get_current_values()

    # assert isinstance(current_values, dict)


# def test_get_data(started_channel: potentiostats.GeneralPotentiostat):
#     something = started_channel.get_data()


def test_stop_channel(
    started_channel: potentiostats.GeneralPotentiostat
    ):
    started_channel.stop_channel()
