"""Parses experiment parameters from  a raw dict form to a instrument-specific
format.

Function set_technique_params() is the only one that should be called externally.
All others can be considered helper functions.
"""

from ctypes import Array, c_float, c_bool, c_int32, create_string_buffer, byref, WinDLL
import json
from typing import Union

from biologic.structures import EccParam, EccParams
from biologic.utils import ParsedParams

with open('biologic\\config.json', 'r') as f:
    settings = json.load(f)

DRIVERPATH = settings['driverpath']

driver = WinDLL(DRIVERPATH + 'EClib64.dll')


def _generate_c_value(
    value: Union[float, bool, int]
    ) -> Union[c_float, c_bool, c_int32]:
    """Generates a ctypes version of value passed to DefineXXXParameter().

    Helper function for _define_parameter().

    Args:
        value (Union[float, bool, int]): Parameter value.

    Returns:
        Union[ctypes.c_float, ctypes.c_bool, ctypes.c_int32]: C-type parameter value.
    """

    _function = {
        int: c_int32,
        float: c_float,
        bool: c_bool
        }[type(value)]

    c_value = _function(value)

    return c_value


def _define_parameter(
    label: str, value: Union[float, bool, int], index: int,
    ecc_param: EccParam
    ):
    """Converts experiment parameters to appropriate to instrument-specific format.

    Helper function for _make_ecc_param().

    NOTE: No explicit return statement bc it uses a c-type buffer.

    Args:
        label (str): Parameter label.
        value (value: Union[float, bool, int]): Parameter value.
        index (int): 
        param (EccParam): _description_
    """

    c_label = create_string_buffer(label.encode())
    c_value = _generate_c_value(value=value)

    _function = {
        int: driver.BL_DefineIntParameter,
        float: driver.BL_DefineSglParameter,
        bool: driver.BL_DefineBoolParameter,
        }[type(value)]

    _function(c_label, c_value, index, byref(ecc_param))


def _make_ecc_param(
    param: ParsedParams, value: Union[float, bool, int], index: int
    ) -> EccParam:
    """Given an ECC_parm template, create and return an EccParam, with its value and index.
    
    Helper function for parse_technique_params().
    """

    ecc_param = EccParam()

    _define_parameter(
        label=param.label,
        value=param.type_(value),
        index=index,
        ecc_param=ecc_param
        )

    return ecc_param


def _ecc_param_array(no_params: int) -> Array[EccParam]:
    """Preallocated a ctypes.Array for EccParams.

    Args:
        no_params (int): Number of parameters.

    Returns:
        Array[EccParam]: Preallocated, empty array.
    """

    ecc_param_array_ = no_params * EccParam

    return ecc_param_array_()


def _consolidate_ecc_params(*ecc_param_tuple: list[EccParam]) -> EccParams:
    """Consolidate EccParam into a single ctypes struct, ready for loading onto instrument.

    Helper function for parse_technique_params().

    Args:
        *ecc_param_tuple (list[EccParam]): Individually prepared technique arguments.

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


def set_technique_params(*technique_params_tuple):
    """Wrapper for initializing the technique params struct.

    Args:
        instrument (:class:`GeneralPotentiostat`): Instrument instance,
            should be an instance of a subclass of
            :class:`GeneralPotentiostat`
    """
    technique_params = dict(technique_params_tuple[0])

    ecc_params = list()
    for [param, value, index] in technique_params.values():
        ecc_param = _make_ecc_param(
            param=param, value=value, index=index
            )
        ecc_params.append(ecc_param)

    c_technique_params = _consolidate_ecc_params(ecc_params)

    return c_technique_params