import ctypes
import pytest

from biologic import techniques
from biologic.structures import EccParam, EccParams
from biologic.utils import parse_raw_params
from tests.params import cp_params

dummy_int = 2
dummy_bool = True
dummy_single = 10.0

dummy_label = 'record_dt'
dummy_value = 1.0
dummy_index = 0
param = EccParam()


def test_generate_c_value_int():
    c_value = techniques._generate_c_value(value=dummy_int)

    assert isinstance(c_value, ctypes.c_int32)


def test_set_voltage_limit():

    config_limit, voltage_limit = techniques._set_voltage_limit(voltage=3.1)

    assert isinstance(config_limit, EccParam)
    assert isinstance(voltage_limit, EccParam)


def test_generate_c_value_bool():
    c_value = techniques._generate_c_value(value=dummy_bool)

    assert isinstance(c_value, ctypes.c_bool)


def test_generate_c_value_single():
    c_value = techniques._generate_c_value(value=dummy_single)

    assert isinstance(c_value, ctypes.c_float)


def test_define_parameter():
    techniques._define_parameter(
        label=dummy_label,
        value=dummy_value,
        index=dummy_index,
        ecc_param=param
        )

    assert isinstance(param, EccParam)
    assert param.ParamType == 2  # Single
    assert param.ParamVal != 0


def test_make_ecc_param():
    ecc_param = techniques._make_ecc_param(
        label=dummy_label, value=dummy_value, index=dummy_index
        )

    assert isinstance(ecc_param, EccParam)
    assert ecc_param.ParamType == 2  # Single
    assert ecc_param.ParamVal != 0


def test_ecc_param_array():
    ecc_param_array = techniques._ecc_param_array(
        no_params=len(cp_params)
        )

    assert len(ecc_param_array) == len(cp_params)
    assert isinstance(ecc_param_array[0], EccParam)


@pytest.fixture
def technique_params_raw() -> list[dict]:
    technique_params_raw, _, _ = parse_raw_params(
        raw_params=cp_params
        )
    return technique_params_raw


@pytest.fixture
def ecc_param_list(technique_params_raw: list[dict]):
    ecc_param_list = list()

    technique_params = technique_params_raw[0]
    for label, value in technique_params.items():
        ecc_param = techniques._make_ecc_param(
            label=label, value=value, index=0
            )
        ecc_param_list.append(ecc_param)

    return ecc_param_list


def test_consolidate_ecc_params(ecc_param_list):
    c_tecc_params = techniques._consolidate_ecc_params(ecc_param_list)

    assert isinstance(c_tecc_params, EccParams)


# Integration
def test_parse_technique_params(technique_params_raw):
    c_tecc_params = techniques.set_technique_params(
        technique_params_raw
        )

    assert isinstance(c_tecc_params, list)
    assert isinstance(c_tecc_params[0], EccParams)
