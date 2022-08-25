"""Low-level helper functions for potentiostat classes and associated techniques."""

import ctypes
import json
import re

from biologic import constants, exceptions

with open('biologic\\config.json', 'r') as f:
    settings = json.load(f)

DRIVERPATH = settings['driverpath']



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
        error_code, ctypes.byref(message),
        ctypes.byref(number_of_chars)
        )

    # # Can't use assert__status_ok() here since it implicitly runs this method.
    if status != 0:
        raise exceptions.BLFindError(error_code=status, message=None)

    return message.value


def _get_tecc_ecc_path(technique_name: str, to_remove: str = '[0-9]') -> str:
    """Generates technique ecc-file path.

    Helper function for parse_raw_params().

    Hacky. Should probably refactor how technique parameters are passed.

    Args:
        technique_name (str): Abbreviated technique name as presented
            in documentation. Example: 'OCV'.

    Returns:
        str: (Relative) technique ecc-file path.
    """

    technique_name_wo_index = re.sub(to_remove, '', technique_name)
    technique_name_wo_index_lowercase = technique_name_wo_index.lower()
    
    return f"{DRIVERPATH}{technique_name_wo_index_lowercase}.ecc"


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


def assert_one_device(c_nbr_dev: ctypes.c_uint32):
    """Checks whether one, and only one, device is connected.

    The library _can_ handle more than one, I just want to
    keep things simple.

    Args:
        c_nbr_dev (ctypes.c_uint32): Number of connected devices.

    Raises:
        exceptions.ECLibCustomException: If 0 or >1 devices connected.
    """

    nbr_dev = c_nbr_dev.value

    if nbr_dev == 1:
        return

    message = f'Number of devices detected ({nbr_dev}) not 1'

    raise exceptions.ECLibCustomException(-9001, message)


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


def parse_potentiostat_search(bytes_string: bytes):
    """Parses USB port and instrument type from potentiostat search.

    Hacky. Might fix later.

    Args:
        bytes_string (bytes): Result of BL_FindEChemUsbDev()

    Returns:
        ip (str): USB-port of connected potentiostat, e.g. 'USB0'.
        instrument_type (str): Instrument type, e.g. 'HCP-1005'.
    """

    search_decoded = bytes_string.raw.decode('utf-8')
    search_split = search_decoded.split('$')
    search_parsed = list()
    for item in search_split:
        split = item.split('\x00')
        merged = ''.join(split)
        
        if len(merged) ==0:
            continue

        search_parsed.append(merged)

    usb_port = search_parsed[0] + search_parsed[1]
    instrument_type = search_parsed[2]

    return usb_port, instrument_type


def parse_raw_params(raw_params: dict):  # -> list(dict, str, str):
    """Wrapper for parsing incoming experiment parameters.

    Args:
        raw_params (dict): Containing exp_id, technique name,
            and detailed params procedure.

    Returns:
        parsed_params (Dict[str, structures.ECC_param]): Parsed experiment parameters.
        tecc_ecc_path (list): List of technique ecc-file paths,
            in sequential order.
        exp_id (str): Experiment ID (corresponding to Drops schema).
    """

    exp_id: str = raw_params['exp_id']
    steps: dict = raw_params['steps']

    techniques_ecc_paths = list()
    parsed_steps = list()

    for technique, params in steps.items():
        tecc_ecc_path = _get_tecc_ecc_path(technique_name=technique)
        techniques_ecc_paths.append(tecc_ecc_path)

        parsed_steps.append(params)

    return parsed_steps, techniques_ecc_paths, exp_id


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
