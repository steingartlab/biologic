from collections import namedtuple
import ctypes

from biologic import constants, exceptions, structures

DataField = namedtuple('DataField', ['name', 'type'])

TechniqueArgument = namedtuple(
    'TechniqueArgument',
    ['label', 'type', 'value', 'check', 'check_argument']
    )


class Technique(object):
    """Base class for techniques
    All specific technique classes inherits from this class.
    Properties available on the object:
    * technique_filename (str): The name of the technique filename
    * args (tuple): Tuple containing the Python version of the
      parameters (see :meth:`.__init__` for details)
    * c_args (array of :class:`.TECCParam`): The c-types array of
      :class:`.TECCParam`
    A specific technique, that inherits from this class **must** overwrite the
    **data_fields** class variable. It describes what the form is, of the data
    that the technique can receive. The variable should be a dict on the
    following form:
    * Some techniques, like :class:`.OCV`, have different data fields depending
      on the series of the instrument. In these cases the dict must contain
      both a 'wmp3' and a 'sp300' key.
    * For cases where the instrument class distinction mentioned above does not
      exist, like e.g. for :class:`.CV`, one can simply define a 'common' key.
    * All three cases above assume that the first field of the returned data is
      a specially formatted ``time`` field, which must not be listed directly.
    * Some techniques, like e.g. :class:`.SPEIS` returns data for two different
      processes, one of which does not contain the ``time`` field (it is
      assumed that the process that contains ``time`` is 0 and the one that
      does not is 1). In this case there must be a 'common' and a 'no-time' key
      (see the implementation of :class:`.SPEIS` for details).
    All of the entries in the dict must point to an list of
    :class:`.DataField` named tuples, where the two arguments are the name and
    the C type of the field (usually :py:class:`c_float <ctypes.c_float>` or
    :py:class:`c_uint32 <ctypes.c_uint32>`). The list of fields must be in the
    order the data fields is specified in the :ref:`specification
    <specification>`.
    """

    data_fields = None

    def __init__(self, args, technique_filename):
        """Initialize a technique
        Args:
            args (tuple): Tuple of technique arguments as TechniqueArgument
                instances
            technique_filename (str): The name of the technique filename.
                .. note:: This must be the vmp3 series version i.e. name.ecc
                  NOT name4.ecc, the replacement of technique file names are
                  taken care of in load technique
        """
        self.args = args
        # The arguments must be converted to an array of TECCParam
        self._c_args = None
        self.technique_filename = technique_filename

    def c_args(self, instrument):
        """Return the arguments struct
        Args:
            instrument (:class:`GeneralPotentiostat`): Instrument instance,
                should be an instance of a subclass of
                :class:`GeneralPotentiostat`
        Returns:
            array of :class:`TECCParam`: An ctypes array of :class:`TECCParam`
        Raises:
            ECLibCustomException: Where the error codes indicate the following:
                * -10000 means that an :class:`TechniqueArgument` failed the
                  'in' test
                * -10001 means that an :class:`TechniqueArgument` failed the
                  '>=' test
                * -10002 means that an :class:`TechniqueArgument` failed the
                  'in_float_range' test
                * -10010 means that it was not possible to find a conversion
                  function for the defined type
                * -10011 means that the value cannot be converted with the
                  conversion function
        """
        if self._c_args is None:
            self._init_c_args(instrument)
        return self._c_args

    def _init_c_args(self, instrument):
        """Initialize the arguments struct
        Args:
            instrument (:class:`GeneralPotentiostat`): Instrument instance,
                should be an instance of a subclass of
                :class:`GeneralPotentiostat`
        """
        # If it is a technique that has multistep arguments, get the number of
        # steps
        step_number = 1
        for arg in self.args:
            if arg.label == 'Step_number':
                step_number = arg.value

        constructed_args = []
        for arg in self.args:
            # Bounds check the argument
            self._check_arg(arg)

            # When type is dict, it means that type is a int_code -> value_str
            # dict, that should be used to translate the str to an int by
            # reversing it be able to look up codes from strs and replace
            # value
            if isinstance(arg.type, dict):
                value = ctypes.reverse_dict(arg.type)[arg.value]
                param = structures.TECCParam()
                instrument.define_integer_parameter(
                    arg.label, value, 0, param
                    )
                constructed_args.append(param)
                continue

            # Get the appropriate conversion function, to populate the EccParam
            stripped_type = arg.type.strip('[]')
            try:
                # Get the conversion method from the instrument instance, this
                # is named something like defined_bool_parameter
                conversion_function = getattr(
                    instrument,
                    'define_{}_parameter'.format(stripped_type)
                    )
            except AttributeError:
                message = 'Unable to find parameter definitions function for '\
                          'type: {}'.format(stripped_type)
                raise exceptions.ECLibCustomException(message, -10010)

            # If the parameter is not a multistep paramter, put the value in a
            # list so we can iterate over it
            if arg.type.startswith('[') and arg.type.endswith(']'):
                values = arg.value
            else:
                values = [arg.value]

            # Iterate over all the steps for the parameter (for most will just
            # be 1)
            for index in range(min(step_number, len(values))):
                param = structures.TECCParam()
                try:
                    conversion_function(
                        arg.label, values[index], index, param
                        )
                except exceptions.ECLibError:
                    message = '{} is not a valid value for conversion to '\
                              'type {} for argument \'{}\''.format(
                                  values[index], stripped_type, arg.label)
                    raise exceptions.ECLibCustomException(
                        message, -10011
                        )
                constructed_args.append(param)

        self._c_args = (structures.TECCParam *
                        len(constructed_args))()
        for index, param in enumerate(constructed_args):
            self._c_args[index] = param

    @staticmethod
    def _check_arg(arg):
        """Perform bounds check on a single argument"""
        if arg.check is None:
            return

        # If the type is not a dict (used for constants) and indicates an array
        elif not isinstance(arg.type, dict) and\
             arg.type.startswith('[') and arg.type.endswith(']'):
            values = arg.value
        else:
            values = [arg.value]

        # Check arguments with a list of accepted values
        if arg.check == 'in':
            for value in values:
                if value not in arg.check_argument:
                    message = '{} is not among the valid values for \'{}\'. '\
                              'Valid values are: {}'.format(
                                  value, arg.label, arg.check_argument)
                    raise exceptions.ECLibCustomException(
                        message, -10000
                        )
            return

        # Perform bounds check, if any
        if arg.check == '>=':
            for value in values:
                if not value >= arg.check_argument:
                    message = 'Value {} for parameter \'{}\' failed '\
                              'check >={}'.format(
                                  value, arg.label, arg.check_argument)
                    raise exceptions.ECLibCustomException(
                        message, -10001
                        )
            return

        # Perform in two parameter range check: A < value < B
        if arg.check == 'in_float_range':
            for value in values:
                if not arg.check_argument[
                    0] <= value <= arg.check_argument[1]:
                    message = 'Value {} for parameter \'{}\' failed '\
                              'check between {} and {}'.format(
                                  value, arg.label,
                                  *arg.check_argument
                              )
                    raise exceptions.ECLibCustomException(
                        message, -10002
                        )
            return

        message = 'Unknown technique parameter check: {}'.format(
            arg.check
            )
        raise exceptions.ECLibCustomException(message, -10002)


# Section 7.2 in the specification
class OCV(Technique):
    """Open Circuit Voltage (OCV) technique class.
    The OCV technique returns data on fields (in order):
    * time (float)
    * Ewe (float)
    * Ece (float) (only wmp3 series hardware)
    """

    #: Data fields definition
    data_fields = {
        'vmp3':
            [
                DataField('Ewe', ctypes.c_float),
                DataField('Ece', ctypes.c_float)
                ],
        'sp300': [DataField('Ewe', ctypes.c_float)],
        }

    def __init__(
        self,
        rest_time_T=10.0,
        record_every_dE=10.0,
        record_every_dT=0.1,
        E_range='KBIO_ERANGE_AUTO'
        ):
        """Initialize the OCV technique
        Args:
            rest_time_t (float): The amount of time to rest (s)
            record_every_dE (float): Record every dE (V)
            record_every_dT  (float): Record evergy dT (s)
            E_range (str): A string describing the E range to use, see the
                :data:`E_RANGES` module variable for possible values
        """
        args = (
            TechniqueArgument(
                'Rest_time_T', 'single', rest_time_T, '>=', 0
                ),
            TechniqueArgument(
                'Record_every_dE', 'single', record_every_dE, '>=', 0
                ),
            TechniqueArgument(
                'Record_every_dT', 'single', record_every_dT, '>=', 0
                ),
            TechniqueArgument(
                'E_Range', constants.VoltageRange, E_range, 'in',
                constants.Erange.values()
                ),
            )
        super(OCV, self).__init__(args, 'ocv.ecc')


# Section 7.3 in the specification
class CV(Technique):
    """Cyclic Voltammetry (CV) technique class.
    The CV technique returns data on fields (in order):
    * time (float)
    * Ec (float)
    * I (float)
    * Ewe (float)
    * cycle (int)
    """

    #:Data fields definition
    data_fields = {
        'common':
            [
                DataField('Ec', ctypes.c_float),
                DataField('I', ctypes.c_float),
                DataField('Ewe', ctypes.c_float),
                DataField('cycle', ctypes.c_uint32),
                ]
        }

    def __init__(
        self,
        vs_initial,
        voltage_step,
        scan_rate,
        record_every_dE=0.1,
        average_over_dE=True,
        N_cycles=0,
        begin_measuring_I=0.5,
        end_measuring_I=1.0,
        I_range='KBIO_IRANGE_AUTO',
        E_range='KBIO_ERANGE_2_5',
        bandwidth='KBIO_BW_5'
        ):
        r"""Initialize the CV technique::
         E_we
         ^
         |       E_1
         |       /\
         |      /  \
         |     /    \      E_f
         | E_i/      \    /
         |            \  /
         |             \/
         |             E_2
         +----------------------> t
        Args:
            vs_initial (list): List (or tuple) of 5 booleans indicating
                whether the current step is vs. the initial one
            voltage_step (list): List (or tuple) of 5 floats (Ei, E1, E2, Ei,
                Ef) indicating the voltage steps (V)
            scan_rate (list): List (or tuple) of 5 floats indicating the scan
                rates (mV/s)
            record_every_dE (float): Record every dE (V)
            average_over_dE (bool): Whether averaging should be performed over
                dE
            N_cycles (int): The number of cycles
            begin_measuring_I (float): Begin step accumulation, 1 is 100%
            end_measuring_I (float): Begin step accumulation, 1 is 100%
            I_Range (str): A string describing the I range, see the
                :data:`I_RANGES` module variable for possible values
            E_range (str): A string describing the E range to use, see the
                :data:`E_RANGES` module variable for possible values
            Bandwidth (str): A string describing the bandwidth setting, see the
                :data:`BANDWIDTHS` module variable for possible values
        Raises:
            ValueError: If vs_initial, voltage_step and scan_rate are not all
                of length 5
        """
        for input_name in ('vs_initial', 'voltage_step', 'scan_rate'):
            if len(locals()[input_name]) != 5:
                message = 'Input \'{}\' must be of length 5, not {}'.format(
                    input_name, len(locals()[input_name])
                    )
                raise ValueError(message)

    # TechniqueArgument = namedtuple(
    # 'TechniqueArgument',
    # ['label', 'type', 'value', 'check', 'check_argument'])

        args = (
            TechniqueArgument(
                'vs_initial', '[bool]', vs_initial, 'in',
                [True, False]
                ),
            TechniqueArgument(
                'Voltage_step', '[single]', voltage_step, None, None
                ),
            TechniqueArgument(
                'Scan_Rate', '[single]', scan_rate, '>=', 0.0
                ),
            TechniqueArgument(
                'Scan_number', 'integer', 2, None, None
                ),
            TechniqueArgument(
                'Record_every_dE', 'single', record_every_dE, '>=',
                0.0
                ),
            TechniqueArgument(
                'Average_over_dE', 'bool', average_over_dE, 'in',
                [True, False]
                ),
            TechniqueArgument(
                'N_Cycles', 'integer', N_cycles, '>=', 0
                ),
            TechniqueArgument(
                'Begin_measuring_I', 'single', begin_measuring_I,
                'in_float_range', (0.0, 1.0)
                ),
            TechniqueArgument(
                'End_measuring_I', 'single', end_measuring_I,
                'in_float_range', (0.0, 1.0)
                ),
            TechniqueArgument(
                'I_Range', constants.CurrentRange, I_range, 'in',
                constants.CurrentRange
                ),
            TechniqueArgument(
                'E_Range', constants.VoltageRange, E_range, 'in',
                constants.VoltageRange
                ),
            TechniqueArgument(
                'Bandwidth', constants.Bandwidth, bandwidth, 'in',
                constants.Bandwidth
                ),
            )
        super(CV, self).__init__(args, 'cv.ecc')


# Section 7.5 in the specification
class CP(Technique):
    """Chrono-Potentiometry (CP) technique class.
    The CP technique returns data on fields (in order):
    * time (float)
    * Ewe (float)
    * I (float)
    * cycle (int)
    """

    #: Data fields definition
    data_fields = {
        'common':
            [
                DataField('Ewe', ctypes.c_float),
                DataField('I', ctypes.c_float),
                DataField('cycle', ctypes.c_uint32),
                ]
        }

    def __init__(
        self,
        current_step=(50E-6,),
        vs_initial=(False,),
        duration_step=(10.0,),
        record_every_dT=0.1,
        record_every_dE=0.001,
        N_cycles=0,
        I_range='KBIO_IRANGE_100uA',
        E_range='KBIO_ERANGE_2_5',
        bandwidth='KBIO_BW_5'
        ):
        """Initialize the CP technique
        NOTE: The current_step, vs_initial and duration_step must be a list or
        tuple with the same length.
        Args:
            current_step (list): List (or tuple) of floats indicating the
                current steps (A). See NOTE above.
            vs_initial (list): List (or tuple) of booleans indicating whether
                the current steps is vs. the initial one. See NOTE above.
            duration_step (list): List (or tuple) of floats indicating the
                duration of each step (s). See NOTE above.
            record_every_dT (float): Record every dT (s)
            record_every_dE (float): Record every dE (V)
            N_cycles (int): The number of times the technique is REPEATED.
                NOTE: This means that the default value is 0 which means that
                the technique will be run once.
            I_Range (str): A string describing the I range, see the
                :data:`I_RANGES` module variable for possible values
            E_range (str): A string describing the E range to use, see the
                :data:`E_RANGES` module variable for possible values
            Bandwidth (str): A string describing the bandwidth setting, see the
                :data:`BANDWIDTHS` module variable for possible values
        Raises:
            ValueError: On bad lengths for the list arguments
        """
        if not len(current_step) == len(vs_initial
                                       ) == len(duration_step):
            message = 'The length of current_step, vs_initial and '\
                      'duration_step must be the same'
            raise ValueError(message)

        # TODO: Edit last three lines
        args = (
            TechniqueArgument(
                'Current_step', '[single]', current_step, None, None
                ),
            TechniqueArgument(
                'vs_initial', '[bool]', vs_initial, 'in',
                [True, False]
                ),
            TechniqueArgument(
                'Duration_step', '[single]', duration_step, '>=', 0
                ),
            TechniqueArgument(
                'Step_number', 'integer', len(current_step), 'in',
                range(99)
                ),
            TechniqueArgument(
                'Record_every_dT', 'single', record_every_dT, '>=', 0
                ),
            TechniqueArgument(
                'Record_every_dE', 'single', record_every_dE, '>=', 0
                ),
            TechniqueArgument(
                'N_Cycles', 'integer', N_cycles, '>=', 0
                ),
            TechniqueArgument(
                'I_Range', constants.CurrentRange('add'), I_range, 'in', constants.CurrentRange(...).value
                ),
            TechniqueArgument(
                'E_Range', constants.VoltageRange, E_range, 'in', constants.VoltageRange.values()
                ),
            TechniqueArgument(
                'Bandwidth', constants.Bandwidth, bandwidth, 'in',
                constants.Bandwidth.values()
                ),
            )
        super(CP, self).__init__(args, 'cp.ecc')


# Section 7.6 in the specification
class CA(Technique):
    """Chrono-Amperometry (CA) technique class.
    The CA technique returns data on fields (in order):
    * time (float)
    * Ewe (float)
    * I (float)
    * cycle (int)
    """

    #:Data fields definition
    data_fields = {
        'common':
            [
                DataField('Ewe', ctypes.c_float),
                DataField('I', ctypes.c_float),
                DataField('cycle', ctypes.c_uint32)
                ]
        }

    def __init__(
        self,
        voltage_step=(0.35,),
        vs_initial=(False,),
        duration_step=(10.0,),
        record_every_dT=0.1,
        record_every_dI=5E-6,
        N_cycles=0,
        I_range='KBIO_IRANGE_AUTO',
        E_range='KBIO_ERANGE_2_5',
        bandwidth='KBIO_BW_5'
        ):
        """Initialize the CA technique
        NOTE: The voltage_step, vs_initial and duration_step must be a list or
        tuple with the same length.
        Args:
            voltage_step (list): List (or tuple) of floats indicating the
                voltage steps (A). See NOTE above.
            vs_initial (list): List (or tuple) of booleans indicating whether
                the current steps is vs. the initial one. See NOTE above.
            duration_step (list): List (or tuple) of floats indicating the
                duration of each step (s). See NOTE above.
            record_every_dT (float): Record every dT (s)
            record_every_dI (float): Record every dI (A)
            N_cycles (int): The number of times the technique is REPEATED.
                NOTE: This means that the default value is 0 which means that
                the technique will be run once.
            I_Range (str): A string describing the I range, see the
                :data:`I_RANGES` module variable for possible values
            E_range (str): A string describing the E range to use, see the
                :data:`E_RANGES` module variable for possible values
            Bandwidth (str): A string describing the bandwidth setting, see the
                :data:`BANDWIDTHS` module variable for possible values
        Raises:
            ValueError: On bad lengths for the list arguments
        """
        if not len(voltage_step) == len(vs_initial
                                       ) == len(duration_step):
            message = 'The length of voltage_step, vs_initial and '\
                      'duration_step must be the same'
            raise ValueError(message)

        args = (
            TechniqueArgument(
                'Voltage_step', '[single]', voltage_step, None, None
                ),
            TechniqueArgument(
                'vs_initial', '[bool]', vs_initial, 'in',
                [True, False]
                ),
            TechniqueArgument(
                'Duration_step', '[single]', duration_step, '>=', 0.0
                ),
            TechniqueArgument(
                'Step_number', 'integer', len(voltage_step), 'in',
                range(99)
                ),
            TechniqueArgument(
                'Record_every_dT', 'single', record_every_dT, '>=',
                0.0
                ),
            TechniqueArgument(
                'Record_every_dI', 'single', record_every_dI, '>=',
                0.0
                ),
            TechniqueArgument(
                'N_Cycles', 'integer', N_cycles, '>=', 0
                ),
            TechniqueArgument(
                'I_Range', I_RANGES, I_range, 'in', I_RANGES.values()
                ),
            TechniqueArgument(
                'E_Range', E_RANGES, E_range, 'in', E_RANGES.values()
                ),
            TechniqueArgument(
                'Bandwidth', BANDWIDTHS, bandwidth, 'in',
                BANDWIDTHS.values()
                ),
            )
        super(CA, self).__init__(args, 'ca.ecc')


#:Technique name to technique class translation dict. IMPORTANT. Add newly
#:implemented techniques to this dictionary
TechniqueIdentifiers = {
    'KBIO_TECHID_OCV': OCV,
    'KBIO_TECHID_CP': CP,
    'KBIO_TECHID_CA': CA,
    'KBIO_TECHID_CV': CV
    }
