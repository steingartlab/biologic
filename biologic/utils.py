"""Low-level helper functions for potentiostat classes and associated techniques."""

import ctypes
import json
from typing import List, TypedDict

from biologic import constants, exceptions, structures

with open('biologic\\config.json', 'r') as f:
    settings = json.load(f)

DRIVERPATH = settings['driverpath']


class ParsedParams(TypedDict):
    key: str
    params: structures.ECC_param


def _get_error_message(
    driver: ctypes.WinDLL, error_code: int, bytes_: int = 255
    ) -> str:
    """Returns error message's corresponding error_code.

    Helper function for assert_status_ok().
    
    Args:
        driver (ctypes.WinDLL): Driver for calling ECLib function.
        error_code (int): The error number to translate.
        bytes_ (int): Number of bytes to allocate to message.
    
    Returns:
        str: Error message's corresponding error_code.
    """

    message = ctypes.create_string_buffer(bytes_)
    number_of_chars = ctypes.c_uint32(bytes_)

    status = driver.BL_GetErrorMsg(
        error_code,
        ctypes.byref(message),
        ctypes.byref(number_of_chars)
        )

    # # Can't use assert__status_ok() here since it implicitly runs this method.
    if status != 0:
        raise exceptions.BLFindError(error_code=status, message=None)

    return message.value


def assert_device_type_ok(
    device_code: int, reference_device: str
    ) -> None:
    """Checks whether returned device code is the expected device.

    Args:
        device_code (int): _description_
        reference_device (st): _description_

    Raises:
        exceptions.ECLibCustomException: If expected and actual
            don't match.
    """

    if constants.Device(device_code).name == reference_device:
        return

    message = f'Device code ({constants.Device(device_code)})'\
              f'returned from the device on connect does not match the'\
              f'device type of class ({reference_device}).'

    raise exceptions.ECLibCustomException(-9000, message)


def assert_status_ok(driver: ctypes.WinDLL, return_code: int) -> None:
    """Checks return code and raises exception if necessary.

    Args:
        driver (ctypes.WinDLL): Driver from ECLib function call.
        return_code (int): Return code from 

    Raises:
        exceptions.ECLibError: If status is not OK.
    """

    if return_code == 0:
        return

    message = _get_error_message(
        driver=driver, error_code=return_code
        )

    raise exceptions.ECLibError(return_code, message)


# def change_ip_address(instrument_ip: str):
#     """Modifies PC's IP-address.

#     NOTE: Not implemented.

#     The PC must be on the same network as the instrument. The
#     instrument's network address varies and the PC's automatically
#     assigned IP-address can clash with the instrument's.

#     This circumvents having to manually change the PC's IP-address
#     in Control Panel and restarting the machine everytime it's
#     connected to a new instrument.

#     Args:
#         instrument_ip (str): Instrument's IP-address,
#             e.g. '192.168.0.1'
#     """

#     ip = ipaddress.IPv4Address(instrument_ip)

#     network = ipaddress.IPv4Network()

#     print(ip._ALL_ONES)


def convert_numeric_to_single(driver, numeric: int) -> float:
    """Converts a numeric (integer) into a float.

    The buffer used to get data out of the device consist only of uint32s
    (most likely to keep its layout simple). To transfer a float, the
    EClib library uses a trick, wherein the value of the float is saved as
    a uint32, by giving the uint32 the integer values, whose
    bit-representation corresponds to the float that it should
    describe. This function is used to convert the integer back to the
    corresponding float.

    NOTE: This trick can also be performed with ctypes along the lines of:
    ``c_float.from_buffer(c_uint32(numeric))``, but in this driver the
    library version is used.

    Args:
        numeric (int): Integer representing a float
    
    Returns:
        float: The float value.
    """
    #
    c_out_float = ctypes.c_float()

    status = driver.BL_ConvertNumericIntoSingle(
        numeric, ctypes.byref(c_out_float)
        )

    assert_status_ok(driver=driver, return_code=status)

    return c_out_float.value


def parse_channel_info(channel_info: dict) -> dict:
    """Parses channel info code to a more readable format.

    NOTE: Not implemented.
    A lot of this is legacy and I'm not strictly sure I need this,
    it's probably just cluttering the code. Might remove.

    Args:
        channel_info (dict): _description_

    Returns:
        dict: _description_
    """

    # Translate code to strings
    channel_info['FirmwareCode(translated)'] = constants.Firmware(
        channel_info['FirmwareCode']
        ).name
    channel_info['AmpCode(translated)'] = constants.Amplifier(
        channel_info['AmpCode']
        ).name
    channel_info['State(translated)'] = constants.State(
        channel_info['State']
        ).name
    channel_info['MaxIRange(translated)'] = constants.CurrentRange(
        channel_info['MaxIRange']
        ).name
    channel_info['MinIRange(translated)'] = constants.CurrentRange(
        channel_info['MinIRange']
        ).name
    channel_info['MaxBandwidth'] = constants.Bandwidth(
        channel_info['MaxBandwidth']
        ).name

    return channel_info


def parse_potentiostat_search(bytes_string: bytes) -> str:
    """Extracts IP-address and instrument type from potentiostat search.

    Hacky. Might fix later. Also can only handle one device.

    Args:
        bytes_string (bytes): Result of BL_FindEChemEthDev()

    Returns:
        ip (str): IP-address of connected potentiostat.
        instrument_type (str): Instrument type, e.g. 'HCP-1005'.
    """

    parsed = bytes_string.raw.decode()

    ip_w_unicode = parsed.split('$')[1]
    instrument_type = parsed.split('$')[5].split(' ')[0]

    # Still contains unicode stuff. Got to remove
    ip = ''
    for character in ip_w_unicode:
        if character.encode('utf-8') == b'\x00':
            continue

        ip += character

    return ip, instrument_type


def parse_payload(
    raw_data: dict,
    desired_keys: list = ['Ewe', 'I', 'ElapsedTime']
    ) -> dict:
    parsed_data = dict()
    """Parses data from instrument before it's dumped to db.

    Args:
        raw_data (dict): Raw data from instrument.
        desired_keys (list, optional): Keys we want in payload.
            Defaults to ['Ewe', 'I', 'ElapsedTime']

    Returns:
        dict: Payload.
    """

    for desired_key in desired_keys:
        parsed_data[desired_key] = raw_data[desired_key]

    return parsed_data


def _get_tecc_ecc_path(technique_name: str) -> str:
    """Generates technique ecc-file path.

    Helper function for parse_raw_params().

    Args:
        technique_name (str): Abbreviated technique name as presented
            in documentation. Example: 'OCV'.

    Returns:
        str: (Relative) technique ecc-file path.
    """
    return f"{DRIVERPATH}{technique_name.lower()}.ecc"


def _parse_exp_params(params: dict) -> ParsedParams:
    """Parses incoming params from a dict to instrument-specific format.

    Helper function for parse_raw_params().

    Args:
        params (dict): Incoming experiment params.

    Returns:
        Dict[str, structures.ECC_param]: _description_
    """

    parsed_params = dict()

    for key, val in params.items():
        label, type_ = val['ecc']
        parsed_params[key] = (
            structures.ECC_param(label, type_),
            val['value'],
            val['index']
        )

    return parsed_params


def parse_raw_params(raw_params: dict):  # -> list(dict, str, str):
    """Wrapper for parsing incoming experiment parameters.

    Args:
        raw_params (dict): Containing exp_id, technique name,
            and detailed params procedure.

    Returns:
        parsed_params (Dict[str, structures.ECC_param]): Parsed experiment parameters.
        tecc_ecc_path (str): Technique ecc-file path.
        exp_id (str): Experiment ID.
    """

    parsed_params = _parse_exp_params(params=raw_params['params'])

    tecc_ecc_path = _get_tecc_ecc_path(
        technique_name=raw_params['technique']
        )

    exp_id = raw_params['exp_id']

    return parsed_params, tecc_ecc_path, exp_id


# def reverse_dict(dict_):
#     """Reverse the key/value status of a dict.
    
#     Inherited from legacy code. TODO: Change to Enum.
#     """
#     return dict([[v, k] for k, v in dict_.items()])


def structure_to_dict(structure: ctypes.Structure) -> dict:
    """Converts a ctypes.Structure to a python dict.
    
    Args:
        structure (ctypes.Structure): Any ctypes.Structure with
            populated _fields_.

    Returns:
        dict: Key-value pairs converted to a python-friendly dictionary.
    """

    out = dict()

    for key, _ in structure._fields_:
        out[key] = getattr(structure, key)

    return out
