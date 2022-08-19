import ctypes
import ipaddress
import json
import pytest

from biologic import exceptions, utils
from biologic.potentiostats import InstrumentFinder

with open('biologic/config.json') as f:
    settings = json.load(f)

driverpath = settings['driver']['driverpath']
driver_example = settings['driver']['example_driver']

dummy_reference_device = 'KBIO_DEV_HCP1005'
dummy_device_code = 18
# Matches the return string format when searching for connected potentiostats.
# See section 5.1 in documentation for details.
dummy_bytes_string = b'Ethernet$192.109.209.180$192.109.209.180$255.255.255.0$00.14.D8.01.08.6E$VMP3#0027$VMP3$0027$x$%'


@pytest.fixture
def driver() -> ctypes.WinDLL:
    driver = ctypes.WinDLL(driverpath + driver_example)

    return driver


def test_get_error_message(driver: ctypes.WinDLL):
    with pytest.raises(exceptions.BLFindError):
        utils._get_error_message(driver=driver, error_code=-2)


def test_assert_device_type_ok():
    utils.assert_device_type_ok(
        device_code=dummy_device_code,
        reference_device=dummy_reference_device
        )


def test_assert_device_type_not_ok():
    with pytest.raises(exceptions.ECLibCustomException):
        utils.assert_device_type_ok(
            device_code=1, reference_device=dummy_reference_device
            )


def test_assert_status_ok(driver: ctypes.WinDLL):
    utils.assert_status_ok(driver=driver, return_code=0)


def test_assert_status_not_ok(driver: ctypes.WinDLL):
    with pytest.raises(exceptions.BLFindError):
        utils.assert_status_ok(driver=driver, return_code=-2)


# @pytest.fixture
# def ip_address():
#     finder = InstrumentFinder()
#     finder.find()

#     return finder.ip_address


# def test_change_ip_address(ip_address: str):
#     utils.change_ip_address(instrument_ip=ip_address)


@pytest.fixture
def dummy_return_string() -> ctypes.create_string_buffer:
    return ctypes.create_string_buffer(dummy_bytes_string)


def test_parse_potentiostat_search(dummy_return_string: ctypes.create_string_buffer):
    ip_address_returned, instrument_type = utils.parse_potentiostat_search(
        bytes_string=dummy_return_string
        )

    assert isinstance(instrument_type, str)
    assert len(instrument_type) > 0

    ip_address = ipaddress.ip_address(ip_address_returned)

    assert isinstance(ip_address, ipaddress.IPv4Address)

# def test_reverse_dict():
#     pass
    # This function is suboptimal and will be rewritten as an Enum

@pytest.fixture
def structure() -> ctypes.Structure:
    class Structure(ctypes.Structure):
        _fields_ = [('key1', ctypes.c_int8), ('key2', ctypes.c_bool)]

    return Structure

def test_structure_to_dict(structure: ctypes.Structure):
    dict_ = utils.structure_to_dict(structure=structure)

    assert isinstance(dict_, dict)
    assert list(dict_.keys()) == ['key1', 'key2']
