import ctypes
import pytest

from biologic import techniques, utils
from biologic.structures import EccParam
from tests.params import raw_params

dummy_int = 2
dummy_bool = True
dummy_single = 10.0

dummy_label = 'duration'
dummy_value = 10.0
dummy_index = 0
param = EccParam()


def test_generate_c_value_int():
    c_value = techniques._generate_c_value(value=dummy_int)

    assert isinstance(c_value, ctypes.c_int32)


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


@pytest.fixture
def params_():
    params_ = utils._parse_exp_params(params=raw_params['params'])

    return params_


def test_make_ecc_param(params_: utils.ParsedParams):
    ecc_param = techniques._make_ecc_param(
        param=params_['duration'][0],
        value=dummy_value,
        index=dummy_index
        )

    assert isinstance(ecc_param, EccParam)
    assert ecc_param.ParamType == 2  # Single
    assert ecc_param.ParamVal != 0


def test_ecc_param_array():
    ecc_param_array = techniques._ecc_param_array(
        no_params=len(raw_params)
        )

    assert len(ecc_param_array) == len(raw_params)
    assert isinstance(ecc_param_array[0], EccParam)


@pytest.fixture
def ecc_param_list(params_: utils.ParsedParams):

    ecc_param_list = list()

    for [param, value, index] in params_.values():
        ecc_param = techniques._make_ecc_param(
            param=param, value=value, index=index
            )
        ecc_param_list.append(ecc_param)

    return ecc_param_list


def test_consolidate_ecc_params(ecc_param_list):
    techniques._consolidate_ecc_params(ecc_param_list)


# Integration
def test_parse_technique_params(params_):
    techniques.set_technique_params(params_)
