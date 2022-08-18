"""The HCP-1005 only contains a single channel, which simplifies testing a bit.
Would have to be expanded slightly if this library were to be generalized.
"""

import ctypes
import ipaddress
import json
import pytest

from biologic import exceptions, potentiostats, techniques

with open('biologic/config.json') as f:
    settings = json.load(f)

driverpath = settings['driver']['driverpath']
driver_example = settings['driver']['example_driver']

# Matches the return string format when searching for connected potentiostats.
# See section 5.1 in documentation for details.
dummy_bytes_string = b'Ethernet$192.109.209.180$192.109.209.180$255.255.255.0$00.14.D8.01.08.6E$VMP3#0027$VMP3$0027$x$%'
dummy_device_code = 18
dummy_reference_device = 'KBIO_DEV_HCP1005'
channels = [1]
# label =
# value =
# index =
# tecc_param =


def test_assert_device_type_ok():
    potentiostats.assert_device_type_ok(
        device_code=dummy_device_code,
        reference_device=dummy_reference_device
        )


def test_assert_device_type_not_ok():
    with pytest.raises(exceptions.ECLibCustomException):
        potentiostats.assert_device_type_ok(
            device_code=1, reference_device=dummy_reference_device
            )


@pytest.fixture
def driver():
    driver = ctypes.WinDLL(driverpath + driver_example)

    return driver


def test_get_error_message(driver):
    with pytest.raises(exceptions.BLFindError):
        potentiostats._get_error_message(driver=driver, error_code=-2)


def test_assert_status_ok(driver):
    potentiostats.assert_status_ok(driver=driver, return_code=0)


def test_assert_status_not_ok(driver):
    with pytest.raises(exceptions.BLFindError):
        potentiostats.assert_status_ok(driver=driver, return_code=-2)


@pytest.fixture
def dummy_return_string():
    return ctypes.create_string_buffer(dummy_bytes_string)


def test_parse_potentiostat_search(dummy_return_string):
    ip_address_returned = potentiostats.parse_potentiostat_search(
        bytes_string=dummy_return_string
        )

    ip_address = ipaddress.ip_address(ip_address_returned)

    assert isinstance(ip_address, ipaddress.IPv4Address)


@pytest.fixture
def finding_instance():
    instance_ = potentiostats.InstrumentFinder()

    return instance_


# Integration
def test_successful_finding(finding_instance):
    ip_address_returned = finding_instance.find()

    assert isinstance(ip_address_returned, str)

    ip_address = ipaddress.ip_address(ip_address_returned)

    assert isinstance(ip_address, ipaddress.IPv4Address)


# ####################################################


@pytest.fixture
def ip_address():
    finding_instance = potentiostats.InstrumentFinder()
    ip_address = finding_instance.find()

    return ip_address


@pytest.fixture
def hcp1005_instance():
    hcp1005_instance = potentiostats.HCP1005()

    return hcp1005_instance


def test_connect(hcp1005_instance, ip_address):
    hcp1005_instance.connect(ip_address=ip_address)


@pytest.fixture
def connection(ip_address):
    hcp1005_instance = potentiostats.HCP1005()
    hcp1005_instance.connect(ip_address=ip_address)

    yield hcp1005_instance

    # Teardown
    hcp1005_instance.disconnect()


def test_test_connection(connection):
    connection.test_connection()


def test_disconnect(connection):
    connection.disconnect()


def test_load_firmware(connection):
    c_results = connection.load_firmware(
        channels=channels, force_reload=True
        )

    assert sum(c_results) == 0


def test_get_channels_plugged(connection):
    channels_plugged = connection.get_channels_plugged()

    assert channels_plugged == [True]


def test_is_channel_plugged(connection):
    is_plugged = connection.is_channel_plugged()

    assert is_plugged is True


def test_get_channel_infos(connection):
    channel_info = connection.get_channel_info()

    assert isinstance(channel_info, dict)


def test_get_message(connection):
    message = connection.get_message()

    assert isinstance(message, str)


# def test_get_error_status(connection):
#     connection.get_error_status()


@pytest.fixture
def technique():
    technique = techniques.CA()

    return technique


def test_load_technique(connection, technique):
    connection.load_technique(technique=technique)

# def test_define_bool_parameter(connection):
#     connection.define_bool_parameter(
#         label=label,
#         value=value,
#         index=index,
#         tecc_param=tecc_param
#     )

# def test_define_single_parameter(connection):

# def test_define_integer_parameter(connection):


# def test_start_channel(connection):
#     connection.start_channel()


@pytest.fixture
def started_channel():
    hcp1005_instance = potentiostats.HCP1005()
    hcp1005_instance.connect(ip_address=ip_address)

    hcp1005_instance.start_channel()

    yield hcp1005_instance

    connection.stop_channel()


# def test_get_current_values(started_channel):
#     current_values = started_channel.get_current_values()

#     assert isinstance(current_values, dict)

# def test_get_data(started_channel):
#     something = started_channel.get_data()


# def test_convert_numeric_to_single(connection):


# def test_stop_channel(started_channel):
#     started_channel.stop_channel()
