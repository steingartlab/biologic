import ctypes
from dataclasses import dataclass
import json

from biologic import constants, structures

with open('biologic/config.json') as f:
    settings = json.load(f)

driverpath = settings['driver']['driverpath']
driver = ctypes.WinDLL(driverpath + 'EClib64.dll')


@dataclass
class ECC_param:
    """ECC param template"""
    label: str
    type_: type

def define_parameter(label: str, value, index: int, parm: structures.EccParam):
    function = {
        int: driver.BL_DefineIntParameter,
        float: driver.BL_DefineSglParameter,
        bool: driver.BL_DefineBoolParameter,
        }[type(value)]
    if isinstance(value, float):
        c_value = ctypes.c_float(value)
    elif isinstance(value, int):
        c_value = ctypes.c_int(value)
    else:
        print('ooooyeah')
    c_label = ctypes.create_string_buffer(label.encode())
    function(c_label, c_value, index, ctypes.byref(parm))


def make_ecc_parm(ecc_parm, value=0, index=0):
    """Given an ECC_parm template, create and return an EccParam, with its value and optional index."""
    param = structures.EccParam()
    # BL_Define<xxx>Parameter
    # .. value is converted to its proper type, which DefineParameter will use
    define_parameter(
        ecc_parm.label, ecc_parm.type_(value), index, param
        )

    return param


def _ecc_param_array(nb):
    array_type = nb * structures.EccParam

    return array_type()


def make_ecc_parms(*ecc_param_list):
    """Create an EccParam array from an EccParam list, and return an EccParams refering to it."""

    no_params = len(ecc_param_list)
    parms_array = _ecc_param_array(no_params)

    for i, param in enumerate(ecc_param_list):
        parms_array[i] = param

    params = structures.EccParams(no_params, parms_array)

    return params


def parse_technique_params(technique_params: dict):
    """Initializes the technique params struct.

    Helper method for get_technique_params().

    Args:
        instrument (:class:`GeneralPotentiostat`): Instrument instance,
            should be an instance of a subclass of
            :class:`GeneralPotentiostat`
    """

    p_duration = make_ecc_parm(
        ecc_parm=technique_params['duration'], value=10.0
        )
    p_record = make_ecc_parm(
        ecc_parm=technique_params['record_dt'], value=0.1
        )
    p_erange = make_ecc_parm(
        ecc_parm=technique_params['E_range'],
        value=constants.VoltageRange['KBIO_ERANGE_AUTO'].value
        )

    c_technique_params = make_ecc_parms(
        p_duration, p_record, p_erange
        )

    return c_technique_params

# class Technique:
#     """Base class for techniques
#     All specific technique classes inherits from this class.
#     Properties available on the object:
#     * technique_filename (str): The name of the technique filename
#     * params (tuple): Tuple containing the Python version of the
#       parameters (see :meth:`.__init__` for details)
#     * c_args (array of :class:`.TECCParam`): The c-types array of
#       :class:`.TECCParam`
#     A specific technique, that inherits from this class **must** overwrite the
#     **data_fields** class variable. It describes what the form is, of the data
#     that the technique can receive. The variable should be a dict on the
#     following form:
#     * Some techniques, like :class:`.OCV`, have different data fields depending
#       on the series of the instrument. In these cases the dict must contain
#       both a 'wmp3' and a 'sp300' key.
#     * For cases where the instrument class distinction mentioned above does not
#       exist, like e.g. for :class:`.CV`, one can simply define a 'common' key.
#     * All three cases above assume that the first field of the returned data is
#       a specially formatted ``time`` field, which must not be listed directly.
#     * Some techniques, like e.g. :class:`.SPEIS` returns data for two different
#       processes, one of which does not contain the ``time`` field (it is
#       assumed that the process that contains ``time`` is 0 and the one that
#       does not is 1). In this case there must be a 'common' and a 'no-time' key
#       (see the implementation of :class:`.SPEIS` for details).
#     All of the entries in the dict must point to an list of
#     :class:`.DataField` named tuples, where the two arguments are the name and
#     the C type of the field (usually :py:class:`c_float <ctypes.c_float>` or
#     :py:class:`c_uint32 <ctypes.c_uint32>`). The list of fields must be in the
#     order the data fields is specified in the :ref:`specification
#     <specification>`.
#     """

#     data_fields = None

#     def __init__(
#         self
#         ):
#         """Initialize a technique.

#         Args:
#             args (namedtuple): Tuple of technique arguments as TechniqueArgument
#                 instances
#             technique_filename (str): The name of the technique filename.
#                 .. note:: This must be the vmp3 series version i.e. name.ecc
#                   NOT name4.ecc, the replacement of technique file names are
#                   taken care of in load technique
#         """

#         # self.params = params
#         self._c_technique_params: structures.TEccParams = None
#         # self.technique_filename = driverpath + technique_filename

#     @property
#     def c_technique_params(self) -> structures.TEccParams:
#         """Return the arguments struct
#         Args:
#             instrument (:class:`GeneralPotentiostat`): Instrument instance,
#                 should be an instance of a subclass of
#                 :class:`GeneralPotentiostat`
#         Returns:
#             array of :class:`TECCParam`: An ctypes array of :class:`TECCParam`
#         Raises:
#             ECLibCustomException: Where the error codes indicate the following:
#                 * -10000 means that an :class:`TechniqueArgument` failed the
#                   'in' test
#                 * -10001 means that an :class:`TechniqueArgument` failed the
#                   '>=' test
#                 * -10002 means that an :class:`TechniqueArgument` failed the
#                   'in_float_range' test
#                 * -10010 means that it was not possible to find a conversion
#                   function for the defined type
#                 * -10011 means that the value cannot be converted with the
#                   conversion function
#         """

#         return self._c_technique_params


# # Section 7.2 in the specification
# class OCV(Technique):
#     """Open Circuit Voltage (OCV) technique class.
#     The OCV technique returns data on fields (in order):
#     * time (float)
#     * Ewe (float)
#     * Ece (float) (only wmp3 series hardware)
#     """

#     #: Data fields definition
#     data_fields = {
#         'vmp3':
#             [
#                 data_field('Ewe', ctypes.c_float),
#                 data_field('Ece', ctypes.c_float)
#                 ]
#         }

#     def __init__(
#         self,
#         rest_time_T=10.0,
#         record_every_dE=10.0,
#         record_every_dT=0.1,
#         E_range='KBIO_ERANGE_AUTO'
#         ):
#         """Initialize the OCV technique
#         Args:
#             rest_time_t (float): The amount of time to rest (s)
#             record_every_dE (float): Record every dE (V)
#             record_every_dT  (float): Record evergy dT (s)
#             E_range (str): A string describing the E range to use, see the
#                 :data:`E_RANGES` module variable for possible values
#         """
#         # ['label', 'type', 'value', 'check', 'check_argument']
#         args = (
#             technique_argument(
#                 'Rest_time_T', 'single', rest_time_T, '>=', 0
#                 ),
#             technique_argument(
#                 'Record_every_dE', '[single]', record_every_dE, '>=', 0
#                 ),
#             technique_argument(
#                 'Record_every_dT', 'single', record_every_dT, '>=', 0
#                 ),
#             technique_argument(
#                 'E_Range', constants.VoltageRange, E_range, 'in', [val for val in constants.VoltageRange.value]
#                 ),
#             )
#         super(OCV, self).__init__(
#             params=args, technique_filename='ocv.ecc'
#             )

# #:E range number to E range name translation dict
# E_RANGES = {
#     0: 'KBIO_ERANGE_2_5',
#     1: 'KBIO_ERANGE_5',
#     2: 'KBIO_ERANGE_10',
#     3: 'KBIO_ERANGE_AUTO'
#     }

# # Section 7.3 in the specification
# class CV(Technique):
#     """Cyclic Voltammetry (CV) technique class.
#     The CV technique returns data on fields (in order):
#     * time (float)
#     * Ec (float)
#     * I (float)
#     * Ewe (float)
#     * cycle (int)
#     """

#     #:Data fields definition
#     data_fields = {
#         'common':
#             [
#                 utils.data_field('Ec', ctypes.c_float),
#                 utils.data_field('I', ctypes.c_float),
#                 utils.data_field('Ewe', ctypes.c_float),
#                 utils.data_field('cycle', ctypes.c_uint32),
#                 ]
#         }

#     def __init__(
#         self,
#         vs_initial,
#         voltage_step,
#         scan_rate,
#         record_every_dE=0.1,
#         average_over_dE=True,
#         N_cycles=0,
#         begin_measuring_I=0.5,
#         end_measuring_I=1.0,
#         I_range='KBIO_IRANGE_AUTO',
#         E_range='KBIO_ERANGE_2_5',
#         bandwidth='KBIO_BW_5'
#         ):
#         r"""Initialize the CV technique::
#          E_we
#          ^
#          |       E_1
#          |       /\
#          |      /  \
#          |     /    \      E_f
#          | E_i/      \    /
#          |            \  /
#          |             \/
#          |             E_2
#          +----------------------> t
#         Args:
#             vs_initial (list): List (or tuple) of 5 booleans indicating
#                 whether the current step is vs. the initial one
#             voltage_step (list): List (or tuple) of 5 floats (Ei, E1, E2, Ei,
#                 Ef) indicating the voltage steps (V)
#             scan_rate (list): List (or tuple) of 5 floats indicating the scan
#                 rates (mV/s)
#             record_every_dE (float): Record every dE (V)
#             average_over_dE (bool): Whether averaging should be performed over
#                 dE
#             N_cycles (int): The number of cycles
#             begin_measuring_I (float): Begin step accumulation, 1 is 100%
#             end_measuring_I (float): Begin step accumulation, 1 is 100%
#             I_Range (str): A string describing the I range, see the
#                 :data:`I_RANGES` module variable for possible values
#             E_range (str): A string describing the E range to use, see the
#                 :data:`E_RANGES` module variable for possible values
#             Bandwidth (str): A string describing the bandwidth setting, see the
#                 :data:`BANDWIDTHS` module variable for possible values
#         Raises:
#             ValueError: If vs_initial, voltage_step and scan_rate are not all
#                 of length 5
#         """
#         for input_name in ('vs_initial', 'voltage_step', 'scan_rate'):
#             if len(locals()[input_name]) != 5:
#                 message = 'Input \'{}\' must be of length 5, not {}'.format(
#                     input_name, len(locals()[input_name])
#                     )
#                 raise ValueError(message)
#         args = (
#             technique_argument(
#                 'vs_initial', '[bool]', vs_initial, 'in',
#                 [True, False]
#                 ),
#             technique_argument(
#                 'Voltage_step', '[single]', voltage_step, None, None
#                 ),
#             technique_argument(
#                 'Scan_Rate', '[single]', scan_rate, '>=', 0.0
#                 ),
#             technique_argument(
#                 'Scan_number', 'integer', 2, None, None
#                 ),
#             technique_argument(
#                 'Record_every_dE', 'single', record_every_dE, '>=',
#                 0.0
#                 ),
#             technique_argument(
#                 'Average_over_dE', 'bool', average_over_dE, 'in',
#                 [True, False]
#                 ),
#             technique_argument(
#                 'N_Cycles', 'integer', N_cycles, '>=', 0
#                 ),
#             technique_argument(
#                 'Begin_measuring_I', 'single', begin_measuring_I,
#                 'in_float_range', (0.0, 1.0)
#                 ),
#             technique_argument(
#                 'End_measuring_I', 'single', end_measuring_I,
#                 'in_float_range', (0.0, 1.0)
#                 ),
#             technique_argument(
#                 'I_Range', I_RANGES, I_range, 'in', I_RANGES.values()
#                 ),
#             technique_argument(
#                 'E_Range', E_RANGES, E_range, 'in', E_RANGES.values()
#                 ),
#             technique_argument(
#                 'Bandwidth', BANDWIDTHS, bandwidth, 'in',
#                 BANDWIDTHS.values()
#                 ),
#             )
#         super(CV, self).__init__(args, 'cv.ecc')

# #:I range number to I range name translation dict
# I_RANGES = {
#     0: 'KBIO_IRANGE_100pA',
#     1: 'KBIO_IRANGE_1nA',
#     2: 'KBIO_IRANGE_10nA',
#     3: 'KBIO_IRANGE_100nA',
#     4: 'KBIO_IRANGE_1uA',
#     5: 'KBIO_IRANGE_10uA',
#     6: 'KBIO_IRANGE_100uA',
#     7: 'KBIO_IRANGE_1mA',
#     8: 'KBIO_IRANGE_10mA',
#     9: 'KBIO_IRANGE_100mA',
#     10: 'KBIO_IRANGE_1A',
#     11: 'KBIO_IRANGE_BOOSTER',
#     12: 'KBIO_IRANGE_AUTO',
#     13: 'KBIO_IRANGE_10pA',  # IRANGE_100pA + Igain x10
#     14: 'KBIO_IRANGE_1pA',  # IRANGE_100pA + Igain x100
#     }
# BANDWIDTHS = {
#     1: 'KBIO_BW_1',
#     2: 'KBIO_BW_2',
#     3: 'KBIO_BW_3',
#     4: 'KBIO_BW_4',
#     5: 'KBIO_BW_5',
#     6: 'KBIO_BW_6',
#     7: 'KBIO_BW_7',
#     8: 'KBIO_BW_8',
#     9: 'KBIO_BW_9'
#     }

# # Section 7.5 in the specification
# class CP(Technique):
#     """Chrono-Potentiometry (CP) technique class.
#     The CP technique returns data on fields (in order):
#     * time (float)
#     * Ewe (float)
#     * I (float)
#     * cycle (int)
#     """

#     #: Data fields definition
#     data_fields = {
#         'common':
#             [
#                 data_field('Ewe', ctypes.c_float),
#                 data_field('I', ctypes.c_float),
#                 data_field('cycle', ctypes.c_uint32),
#                 ]
#         }

#     def __init__(
#         self,
#         current_step=(50E-6,),
#         vs_initial=(False,),
#         duration_step=(10.0,),
#         record_every_dT=0.1,
#         record_every_dE=0.001,
#         N_cycles=0,
#         I_range='KBIO_IRANGE_100uA',
#         E_range='KBIO_ERANGE_2_5',
#         bandwidth='KBIO_BW_5'
#         ):
#         """Initialize the CP technique
#         NOTE: The current_step, vs_initial and duration_step must be a list or
#         tuple with the same length.
#         Args:
#             current_step (list): List (or tuple) of floats indicating the
#                 current steps (A). See NOTE above.
#             vs_initial (list): List (or tuple) of booleans indicating whether
#                 the current steps is vs. the initial one. See NOTE above.
#             duration_step (list): List (or tuple) of floats indicating the
#                 duration of each step (s). See NOTE above.
#             record_every_dT (float): Record every dT (s)
#             record_every_dE (float): Record every dE (V)
#             N_cycles (int): The number of times the technique is REPEATED.
#                 NOTE: This means that the default value is 0 which means that
#                 the technique will be run once.
#             I_Range (str): A string describing the I range, see the
#                 :data:`I_RANGES` module variable for possible values
#             E_range (str): A string describing the E range to use, see the
#                 :data:`E_RANGES` module variable for possible values
#             Bandwidth (str): A string describing the bandwidth setting, see the
#                 :data:`BANDWIDTHS` module variable for possible values
#         Raises:
#             ValueError: On bad lengths for the list arguments
#         """
#         if not len(current_step) == len(vs_initial
#                                        ) == len(duration_step):
#             message = 'The length of current_step, vs_initial and '\
#                       'duration_step must be the same'
#             raise ValueError(message)

#         # TODO: Edit last three lines
#         args = (
#             technique_argument(
#                 'Current_step', '[single]', current_step, None, None
#                 ),
#             technique_argument(
#                 'vs_initial', '[bool]', vs_initial, 'in',
#                 [True, False]
#                 ),
#             technique_argument(
#                 'Duration_step', '[single]', duration_step, '>=', 0
#                 ),
#             technique_argument(
#                 'Step_number', 'integer', len(current_step), 'in',
#                 range(99)
#                 ),
#             technique_argument(
#                 'Record_every_dT', 'single', record_every_dT, '>=', 0
#                 ),
#             technique_argument(
#                 'Record_every_dE', 'single', record_every_dE, '>=', 0
#                 ),
#             technique_argument(
#                 'N_Cycles', 'integer', N_cycles, '>=', 0
#                 ),
#             technique_argument(
#                 'I_Range', constants.CurrentRange('add'), I_range,
#                 'in',
#                 constants.CurrentRange(...).value
#                 ),
#             technique_argument(
#                 'E_Range', constants.VoltageRange, E_range, 'in',
#                 constants.VoltageRange.values()
#                 ),
#             technique_argument(
#                 'Bandwidth', constants.Bandwidth, bandwidth, 'in',
#                 constants.Bandwidth.values()
#                 ),
#             )
#         super(CP, self).__init__(args, 'cp.ecc')

# # Section 7.6 in the specification
# class CA(Technique):
#     """Chrono-Amperometry (CA) technique class.
#     The CA technique returns data on fields (in order):
#     * time (float)
#     * Ewe (float)
#     * I (float)
#     * cycle (int)
#     """

#     #:Data fields definition
#     data_fields = {
#         'common':
#             [
#                 data_field('Ewe', ctypes.c_float),
#                 data_field('I', ctypes.c_float),
#                 data_field('cycle', ctypes.c_uint32)
#                 ]
#         }

#     def __init__(
#         self,
#         voltage_step=(0.35,),
#         vs_initial=(False,),
#         duration_step=(10.0,),
#         record_every_dT=0.1,
#         record_every_dI=5E-6,
#         N_cycles=0,
#         I_range='KBIO_IRANGE_AUTO',
#         E_range='KBIO_ERANGE_2_5',
#         bandwidth='KBIO_BW_5'
#         ):
#         """Initialize the CA technique
#         NOTE: The voltage_step, vs_initial and duration_step must be a list or
#         tuple with the same length.
#         Args:
#             voltage_step (list): List (or tuple) of floats indicating the
#                 voltage steps (A). See NOTE above.
#             vs_initial (list): List (or tuple) of booleans indicating whether
#                 the current steps is vs. the initial one. See NOTE above.
#             duration_step (list): List (or tuple) of floats indicating the
#                 duration of each step (s). See NOTE above.
#             record_every_dT (float): Record every dT (s)
#             record_every_dI (float): Record every dI (A)
#             N_cycles (int): The number of times the technique is REPEATED.
#                 NOTE: This means that the default value is 0 which means that
#                 the technique will be run once.
#             I_Range (str): A string describing the I range, see the
#                 :data:`I_RANGES` module variable for possible values
#             E_range (str): A string describing the E range to use, see the
#                 :data:`E_RANGES` module variable for possible values
#             Bandwidth (str): A string describing the bandwidth setting, see the
#                 :data:`BANDWIDTHS` module variable for possible values
#         Raises:
#             ValueError: On bad lengths for the list arguments
#         """
#         if not len(voltage_step) == len(vs_initial
#                                        ) == len(duration_step):
#             message = 'The length of voltage_step, vs_initial and '\
#                       'duration_step must be the same'
#             raise ValueError(message)

#         args = (
#             technique_argument(
#                 'Voltage_step', '[single]', voltage_step, None, None
#                 ),
#             technique_argument(
#                 'vs_initial', '[bool]', vs_initial, 'in',
#                 [True, False]
#                 ),
#             technique_argument(
#                 'Duration_step', '[single]', duration_step, '>=', 0.0
#                 ),
#             technique_argument(
#                 'Step_number', 'integer', len(voltage_step), 'in',
#                 range(99)
#                 ),
#             technique_argument(
#                 'Record_every_dT', 'single', record_every_dT, '>=',
#                 0.0
#                 ),
#             technique_argument(
#                 'Record_every_dI', 'single', record_every_dI, '>=',
#                 0.0
#                 ),
#             technique_argument(
#                 'N_Cycles', 'integer', N_cycles, '>=', 0
#                 ),
#             technique_argument(
#                 'I_Range', I_RANGES, I_range, 'in', I_RANGES.values()
#                 ),
#             technique_argument(
#                 'E_Range', E_RANGES, E_range, 'in', E_RANGES.values()
#                 ),
#             technique_argument(
#                 'Bandwidth', BANDWIDTHS, bandwidth, 'in',
#                 BANDWIDTHS.values()
#                 ),
#             )
#         super(CA, self).__init__(args, 'ca.ecc')

# #:Technique name to technique class translation dict. IMPORTANT. Add newly
# #:implemented techniques to this dictionary
# TechniqueIdentifiers = {
#     'KBIO_TECHID_OCV': OCV,
#     'KBIO_TECHID_CP': CP,
#     'KBIO_TECHID_CA': CA,
#     'KBIO_TECHID_CV': CV
#     }

# def get_conversion_function(param: dict):
#     print(param.type)
#     stripped_type = param.type.strip('[]')
#     print(stripped_type)

#     # try:
#     #     # Get the conversion method from the instrument instance, this
#     #     # is named something like defined_bool_parameter
#     #     conversion_function = getattr(
#     #         instrument,
#     #         f'define_{stripped_type}_param'
#     #     )
#     #     print(type(conversion_function))
#     #     return conversion_function

#     # except AttributeError:
#     #     raise exceptions.ECLibCustomException(error_code=-10010)

# def generate_integer_param(param: dict):
#     # When type is dict, it means that type is a int_code -> value_str
#     # dict, that should be used to translate the str to an int by
#     # reversing it be able to look up codes from strs and replace
#     # value
#     value = param.type[param.value].value # utils.reverse_dict(param.type)[param.value]
#     print(value)
#     tecc_param = structures.TEccParam()
#     potentiostats.define_integer_param(
#         label=param.label,
#         value=value,
#         index=0,
#         tecc_param=tecc_param
#         )

#     return tecc_param
