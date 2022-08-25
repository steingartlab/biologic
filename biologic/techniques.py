"""Parses experiment parameters from a raw dict form to a instrument-specific
format (ctypes.Structure).

Function set_technique_params() is the only one that should be called externally.
All others are helper functions, and are as such prepended by an underscore.

The functions are not sorted alphabetically but in the order of highest-level
to lowest level.
"""

from ctypes import Array, c_float, c_bool, c_int32, create_string_buffer, byref, WinDLL
import json
from typing import Union

from biologic.structures import EccParam, EccParams

with open('biologic\\config.json', 'r') as f:
    settings = json.load(f)

DRIVERPATH = settings['driverpath']

driver = WinDLL(DRIVERPATH + 'EClib64.dll')


def set_technique_params(techniques: list[dict[str, Union[float, int, bool]]]) -> list[EccParams]:
    """Wrapper for initializing the technique params struct.

    Args:
        techniques (list[dict[str, Union[float, int, bool]]]): Techniques,
            as passed from utils.parse_raw_params().

    Returns:
        EccParams: Technique parameters ready to be passed
            to potentiostats.load_technique().

    Example:
        raw_params = {
            'exp_id': 'brix2/test/test',
            'steps': {
                'OCV': {
                    'Rest_time_T': 3.0,
                    'Record_every_dT': 1.0,
                    }
                }
            }
        parsed_params, _, _ = utils.parse_raw_params(raw_params)
        c_technique_params = set_technique_params(parsed_params)
    """

    c_technique_params = list()

    for technique in techniques:
        ecc_param_list = list()

        # For implicit sampling rate (1s). Previously every technique needed this
        # passed explicitly.
        if 'Record_every_dT' not in technique.keys() and 'loop_N_times' not in technique.keys():
            technique['Record_every_dT'] = 1.0

        # If I understand it correctly, index>0 is only useful for techniques with
        # multiple steps. Will implement if need be
        for label, value in technique.items():
            ecc_param = _make_ecc_param(label=label, value=value, index=0)
            ecc_param_list.append(ecc_param)

        ecc_params = _consolidate_ecc_params(ecc_param_list)
        c_technique_params.append(ecc_params)

    return c_technique_params


def _consolidate_ecc_params(*ecc_param_tuple: tuple[EccParam]) -> EccParams:
    """Consolidate EccParam into a single ctypes.Structure.

    Helper function for parse_technique_params(). Called once for each technique.

    Args:
        *ecc_param_tuple (tuple[EccParam]): Individually prepared technique arguments.

    Returns:
        EccParams: Technique parameters ready to be passed
            to potentiostats.load_technique().
    """

    ecc_param_list = list(ecc_param_tuple[0])
    no_params = len(ecc_param_list)
    params_array = _ecc_param_array(no_params=no_params)

    for i, param in enumerate(ecc_param_list):
        params_array[i] = param

    return EccParams(no_params, params_array)


def _ecc_param_array(no_params: int) -> Array[EccParam]:
    """A preallocated ctypes.Array for EccParams.

    Helper function for _consolidate_ecc_params().

    Args:
        no_params (int): Number of parameters.

    Returns:
        Array[EccParam]: Preallocated, empty array.
    """

    ecc_param_array_ = no_params * EccParam

    return ecc_param_array_()


def _make_ecc_param(label: str, value: Union[float, bool, int], index: int) -> EccParam:
    """Given an ECC param dict, create and return an EccParam.
    
    Helper function for parse_technique_params().

    Args:
        label (str): Step label, e.g. 'Rest_time_T'. NOTE: Case-sensitive.
        value (Union[float, bool, int]): So, either a float, bool, or an int.
            The step value.
        index (int): Technique index. Used for linked techniques.

    Returns:
        EccParam: A ctypes.Structure, refer to class definition.
    """

    ecc_param = EccParam()

    _define_parameter(
        label=label,
        value=value,
        ecc_param=ecc_param,
        index=index
    )

    return ecc_param


def _define_parameter(label: str, value: Union[float, bool, int], ecc_param: EccParam, index: int):
    """Converts experiment parameters to appropriate to instrument-specific format.

    Helper function for _make_ecc_param().

    NOTE: No explicit return statement bc it uses a c-type buffer.

    Args:
        label (str): Step label, e.g. 'Rest_time_T'. NOTE: Case-sensitive.
        value (Union[float, bool, int]): So, either a float, bool, or an int.
            The step value.
        index (int): Technique index. Used for linked techniques.
        EccParam: An _empty_ ctypes.Structure, refer to class definition.
    """

    c_label = create_string_buffer(label.encode())
    c_value = _generate_c_value(value=value)

    _function = {
        int: driver.BL_DefineIntParameter,
        float: driver.BL_DefineSglParameter,
        bool: driver.BL_DefineBoolParameter,
        }[type(value)]

    _function(c_label, c_value, index, byref(ecc_param))


def _generate_c_value(
    value: Union[float, bool, int]
    ) -> Union[c_float, c_bool, c_int32]:
    """Generates a ctypes version of value passed to DefineXXXParameter().

    Helper function for _define_parameter().

    Args:
        value (Union[float, bool, int]): So, either a float, bool, or an int.
            The step value.

    Returns:
        Union[ctypes.c_float, ctypes.c_bool, ctypes.c_int32]: ctypes step value.
    """

    _function = {
        int: c_int32,
        float: c_float,
        bool: c_bool
        }[type(value)]

    c_value = _function(value)

    return c_value