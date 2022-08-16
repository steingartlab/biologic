import ctypes
import ipaddress
import json
import pytest

from biologic import exceptions, potentiostats

with open('biologic/config.json') as f:
    settings = json.load(f)

driverpath = settings['driver']['driverpath']
driver_example = settings['driver']['example_driver']

# Matches the return string format when searching for connected potentiostats.
# See section 5.1 in documentation for details.
dummy_bytes_string = b'Ethernet$192.109.209.180$192.109.209.180$255.255.255.0$00.14.D8.01.08.6E$VMP3#0027$VMP3$0027$x$%'

# Unit

# def test_assert_device_type_ok(driver):
#     pass

# def test_assert_device_type_not_ok():
#     pass


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

#Ethernet$192.168.0.1$192.168.0.1$255.255.255.0$00.14.D8.01.03.F7$HCP-1005
# #1002            $HCP-1005$1002            $x