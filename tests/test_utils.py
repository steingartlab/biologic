import ctypes
import ipaddress
import json
import pytest

from biologic import constants, exceptions, utils
from tests.params import raw_params, dummy_raw_data, dummy_bytes_string

with open('biologic/config.json') as f:
    config = json.load(f)

driverpath = config['driverpath']
driver_example = 'EClib64.dll'

dummy_reference_device = 'KBIO_DEV_HCP1005'
dummy_device_code = 18
int_representing_a_float = 100

dummy_tecc_ecc_path = 'drivers\\ocv.ecc'
dummy_exp_id = 'brix2/test/test'

dummy_voltage = 3.1290981769561768


@pytest.fixture
def driver() -> ctypes.WinDLL:
    driver = ctypes.WinDLL(driverpath + driver_example)

    return driver


def test_get_error_message(driver: ctypes.WinDLL):
    message = utils._get_error_message(driver=driver, error_code=-2)

    assert message.decode() == "connection in progress"


def test_assert_device_type_ok():
    utils.assert_device_type_ok(
        device_code=dummy_device_code,
        reference_device=dummy_reference_device
        )


def test_assert_device_type_not_ok():
    with pytest.raises(exceptions.ECLibCustomException):
        utils.assert_device_type_ok(
            device_code=14, reference_device=dummy_reference_device
            )


def test_assert_status_ok(driver: ctypes.WinDLL):
    utils.assert_status_ok(driver=driver, return_code=0)


def test_assert_status_not_ok(driver: ctypes.WinDLL):
    with pytest.raises(exceptions.ECLibError):
        utils.assert_status_ok(driver=driver, return_code=-2)


def test_convert_numeric_to_single(driver):
    utils.convert_numeric_to_single(
        driver=driver, numeric=int_representing_a_float
        )


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


def test_parse_potentiostat_search(
    dummy_return_string: ctypes.create_string_buffer
    ):
    ip_address_returned, instrument_type = utils.parse_potentiostat_search(
        bytes_string=dummy_return_string
        )

    assert isinstance(instrument_type, str)
    assert len(instrument_type) > 0

    ip_address = ipaddress.ip_address(ip_address_returned)

    assert isinstance(ip_address, ipaddress.IPv4Address)


def test_parse_payload():
    payload = utils.parse_payload(raw_data=dummy_raw_data)

    assert isinstance(payload, dict)
    assert payload['Ewe'] == dummy_voltage
    assert len(payload) == 3


def test_parse_exp_params():
    parsed_params = utils._parse_exp_params(params=raw_params['params'])

    assert isinstance(parsed_params, dict)
    assert isinstance(
        parsed_params['duration'][0], constants.ECC_param
        )


def test_get_tecc_ecc_path():
    tecc_ecc_path = utils._get_tecc_ecc_path(
        technique_name=raw_params['technique']
        )

    assert tecc_ecc_path == dummy_tecc_ecc_path


def test_parse_raw_params():
    parsed_params, tecc_ecc_path, exp_id = utils.parse_raw_params(
        raw_params=raw_params
    )

    assert isinstance(parsed_params, dict)
    assert isinstance(
        parsed_params['duration'][0], constants.ECC_param
        )
    assert tecc_ecc_path == dummy_tecc_ecc_path
    assert exp_id == dummy_exp_id


@pytest.fixture
def structure() -> ctypes.Structure:

    class Structure(ctypes.Structure):
        _fields_ = [('key1', ctypes.c_int8), ('key2', ctypes.c_bool)]

    return Structure


def test_structure_to_dict(structure: ctypes.Structure):
    dict_ = utils.structure_to_dict(structure=structure)

    assert isinstance(dict_, dict)
    assert list(dict_.keys()) == ['key1', 'key2']
