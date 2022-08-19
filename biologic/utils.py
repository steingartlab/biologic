"""Low-level helper functions for potentiostat classes and associated techniques."""

import ctypes
from enum import Enum
import ipaddress

from biologic import constants, exceptions


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
        ctypes.c_int32(error_code), ctypes.byref(message),
        ctypes.byref(number_of_chars)
        )

    # Can't use assert__status_ok() here since it implicitly runs this method.
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


def assert_technique_argument_ok(param):
    """Perform bounds check on a single argument"""

    if param.check is None:
        return

    # If the type is not a dict (used for constants) and indicates an array
    if isinstance(param.type, Enum):
        values = param.value
    elif param.type.startswith('['):
        values = param.value
    else:
        values = [param.value]

    # Check arguments with a list of accepted values
    if param.check == 'in':
        for value in values:
            if value not in param.check_argument:
                message = f'{value} is not among the valid values for' \
                          f'{param.label}. Valid values are: {param.check_argument}'
                raise exceptions.ECLibCustomException(message, -10000)
        return

    # Perform bounds check, if any
    if param.check == '>=':
        print('\n', values)
        for value in values:
            if not value >= param.check_argument:
                message = 'Value {} for parameter \'{}\' failed '\
                            'check >={}'.format(
                                value, param.label, param.check_argument)
                raise exceptions.ECLibCustomException(message, -10001)
        return

    # Perform in two parameter range check: A < value < B
    if param.check == 'in_float_range':
        for value in values:
            if not param.check_argument[
                0] <= value <= param.check_argument[1]:
                message = 'Value {} for parameter \'{}\' failed '\
                            'check between {} and {}'.format(
                                value, param.label,
                                *param.check_argument
                            )
                raise exceptions.ECLibCustomException(message, -10002)
        return

    message = 'Unknown technique parameter check: {}'.format(
        param.check
        )
    raise exceptions.ECLibCustomException(message, -10002)


def change_ip_address(instrument_ip: str):
    """Modifies PC's IP-address.

    The PC must be on the same network as the instrument. The
    instrument's network address varies and the PC's automatically
    assigned IP-address can clash with the instrument's.
    
    This circumvents having to manually change the PC's IP-address
    in Control Panel and restarting the machine everytime it's
    connected to a new instrument.

    Args:
        instrument_ip (str): Instrument's IP-address, 
            e.g. '192.168.0.1'
    """

    ip = ipaddress.IPv4Address(instrument_ip)

    network = ipaddress.IPv4Network()

    print(ip._ALL_ONES)


def parse_channel_info(channel_info: dict) -> dict:
    """Parses channel info code to a more readable format.

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
        str: IP-address of connected potentiostat.
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


def reverse_dict(dict_):
    """Reverse the key/value status of a dict.
    
    Inherited from legacy code. TODO: Change to Enum.
    """
    return dict([[v, k] for k, v in dict_.items()])


def structure_to_dict(structure: ctypes.Structure) -> dict:
    """Convert a ctypes.Structure to a python dict."""

    out = dict()

    for key, _ in structure._fields_:
        out[key] = getattr(structure, key)

    return out
