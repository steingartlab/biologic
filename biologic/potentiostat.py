import ctypes
import os

class GeneralPotentiostat(object):
    """General driver for the potentiostats that can be controlled by the
    EC-lib DLL
    A driver for a specific potentiostat type will inherit from this class.
    Raises:
        ECLibError: All regular methods in this class use the EC-lib DLL
            communications library to talk with the equipment and they will
            raise this exception if this library reports an error. It will not
            be explicitly mentioned in every single method.
    """

    def __init__(self, type_, address, EClib_dll_path, series: str = 'vmp3'):
        """Initialize the potentiostat driver
        Args:
            type_ (str): The device type e.g. 'KBIO_DEV_SP150'
            address (str): The address of the instrument, either IP address or
                USB0, USB1 etc
            EClib_dll_path (str): The path to the EClib DLL. The default
                directory of the DLL is
                C:\\EC-Lab Development Package\\EC-Lab Development Package\\
                and the filename is either EClib64.dll or EClib.dll depending
                on whether the operating system is 64 of 32 Windows
                respectively. If no value is given the default location will be
                used and the 32/64 bit status inferred.
            series (str, optional): One of two series of instruments, either
                'sp300' or 'vmp3'. Defaults to 'vmp3'.
        Raises:
            WindowsError: If the EClib DLL cannot be found
        """
        self._type = type_

        self.series = series  # HCP-1005 is in this series (as opposed to SP-300)

        self.address = address
        self._id = None
        self._device_info = None

        # Load the EClib dll
        if EClib_dll_path is None:
            EClib_dll_path = \
                'C:\\EC-Lab Development Package\\EC-Lab Development Package\\'

            # Appearently, this is the way to check whether this is 64 bit
            # Windows: http://stackoverflow.com/questions/2208828/
            # detect-64bit-os-windows-in-python. NOTE: That it is not
            # sufficient to use platform.architecture(), since that will return
            # the 32/64 bit value of Python NOT the OS
            if 'PROGRAMFILES(X86)' in os.environ:
                EClib_dll_path += 'EClib64.dll'
            else:
                EClib_dll_path += 'EClib.dll'

        self._eclib = ctypes.WinDLL(EClib_dll_path)

    @property
    def id_number(self):  # pylint: disable=C0103
        """Return the device id as an int"""
        if self._id is None:
            return None
        return self._id.value

    @property
    def device_info(self):
        """Return the device information.
        Returns:
            dict or None: The device information as a dict or None if the
                device is not connected.
        """
        if self._device_info is not None:
            out = ctypes.structure_to_dict(self._device_info)
            out['DeviceCode(translated)'] = DEVICE_CODES[out['DeviceCode']]
            return out

    # General functions
    def get_lib_version(self):
        """Return the version of the EClib communications library.
        Returns:
            str: The version string for the library
        """
        size = ctypes.c_uint32(255)
        version = ctypes.create_string_buffer(255)
        ret = self._eclib.BL_GetLibVersion(ctypes.byref(version), ctypes.byref(size))
        self.check_eclib_return_code(ret)
        return version.value

    def get_error_message(self, error_code):
        """Return the error message corresponding to error_code
        Args:
            error_code (int): The error number to translate
        Returns:
            str: The error message corresponding to error_code
        """
        message = ctypes.create_string_buffer(255)
        number_of_chars = ctypes.c_uint32(255)
        ret = self._eclib.BL_GetErrorMsg(
            error_code,
            ctypes.byref(message),
            ctypes.byref(number_of_chars)
        )
        # IMPORTANT, we cannot use, self.check_eclib_return_code here, since
        # that internally use this method, thus we have the potential for an
        # infinite loop
        if ret < 0:
            err_msg = 'The error message is unknown, because it is the '\
                      'method to retrieve the error message with that fails. '\
                      'See the error codes sections (5.4) of the EC-Lab '\
                      'development package documentation to get the meaning '\
                      'of the error code.'
            raise ECLibError(err_msg, ret)
        return message.value

    # Communications functions
    def connect(self, timeout=5):
        """Connect to the instrument and return the device info.
        Args:
            timeout (int): The connect timeout
        Returns:
            dict or None: The device information as a dict or None if the
                device is not connected.
        Raises:
            ECLibCustomException: If this class does not match the device type
        """
        address = ctypes.create_string_buffer(self.address)
        self._id = ctypes.c_int32()
        device_info = DeviceInfos()
        ret = self._eclib.BL_Connect(ctypes.byref(address), timeout,
                                     ctypes.byref(self._id),
                                     ctypes.byref(device_info))
        self.check_eclib_return_code(ret)
        if DEVICE_CODES[device_info.DeviceCode] != self._type:
            message = 'The device type ({}) returned from the device '\
                      'on connect does not match the device type of '\
                      'the class ({})'.format(
                        DEVICE_CODES[device_info.DeviceCode],
                        self._type)
            raise ECLibCustomException(-9000, message)
        self._device_info = device_info
        return self.device_info

    def disconnect(self):
        """Disconnect from the device"""
        ret = self._eclib.BL_Disconnect(self._id)
        self.check_eclib_return_code(ret)
        self._id = None
        self._device_info = None

    def test_connection(self):
        """Test the connection"""
        ret = self._eclib.BL_TestConnection(self._id)
        self.check_eclib_return_code(ret)

    # Firmware functions
    def load_firmware(self, channels, force_reload=False):
        """Load the library firmware on the specified channels, if it is not
        already loaded
        Args:
            channels (list): List with 1 integer per channel (usually 16),
                (0=False and 1=True), that indicates which channels the
                firmware should be loaded on. NOTE: The length of the list must
                correspond to the number of channels supported by the
                equipment, not the number of channels installed. In most cases
                it will be 16.
            force_reload (bool): If True the firmware is forcefully reloaded,
                even if it was already loaded
        Returns:
            list: List of integers indicating the success of loading the
                firmware on the specified channel. 0 is success and negative
                values are errors, whose error message can be retrieved with
                the get_error_message method.
        """
        c_results = (ctypes.c_int32 * len(channels))()
        p_results = ctypes.cast(c_results, ctypes.POINTER(ctypes.c_int32))

        c_channels = (ctypes.c_uint8 * len(channels))()
        for index in range(len(channels)):
            c_channels[index] = channels[index]
        p_channels = ctypes.cast(c_channels, ctypes.POINTER(ctypes.c_uint8))

        ret = self._eclib.BL_LoadFirmware(
            self._id, p_channels, p_results, len(channels), False,
            force_reload, None, None)
        self.check_eclib_return_code(ret)
        return list(c_results)

    # Channel information functions
    def is_channel_plugged(self, channel):
        """Test if the selected channel is plugged.
        Args:
            channel (int): Selected channel (0-15 on most devices)
        Returns:
            bool: Whether the channel is plugged
        """
        result = self._eclib.BL_IsChannelPlugged(self._id, channel)
        return result == 1

    def get_channels_plugged(self):
        """Get information about which channels are plugged.
        Returns:
            (list): A list of channel plugged statusses as booleans
        """
        status = (ctypes.c_uint8 * 16)()
        pstatus = ctypes.cast(status, ctypes.POINTER(ctypes.c_uint8))
        ret = self._eclib.BL_GetChannelsPlugged(self._id, pstatus, 16)
        self.check_eclib_return_code(ret)
        return [result == 1 for result in status]

    def get_channel_infos(self, channel):
        """Get information about the specified channel.
        Args:
            channel (int): Selected channel, zero based (0-15 on most devices)
        Returns:
            dict: Channel infos dict. The dict is created by conversion from
                :class:`.ChannelInfos` class (type
                :py:class:`ctypes.Structure`). See the documentation for that
                class for a list of available dict items. Besides the items
                listed, there are extra items for all the original items whose
                value can be converted from an integer code to a string. The
                keys for those values are suffixed by (translated).
        """
        channel_info = ChannelInfos()
        self._eclib.BL_GetChannelInfos(self._id, channel,
                                       byref(channel_info))
        out = ctypes.structure_to_dict(channel_info)

        # Translate code to strings
        out['FirmwareCode(translated)'] = \
            FIRMWARE_CODES[out['FirmwareCode']]
        out['AmpCode(translated)'] = AMP_CODES.get(out['AmpCode'])
        out['State(translated)'] = STATES.get(out['State'])
        out['MaxIRange(translated)'] = I_RANGES.get(out['MaxIRange'])
        out['MinIRange(translated)'] = I_RANGES.get(out['MinIRange'])
        out['MaxBandwidth'] = BANDWIDTHS.get(out['MaxBandwidth'])
        return out

    def get_message(self, channel):
        """ Return a message from the firmware of a channel """
        size = ctypes.c_uint32(255)
        message = ctypes.create_string_buffer(255)
        ret = self._eclib.BL_GetMessage(self._id, channel,
                                        ctypes.byref(message),
                                        ctypes.byref(size))
        self.check_eclib_return_code(ret)
        return message.value

    # Technique functions:
    def load_technique(self, channel, technique, first=True, last=True):
        """Load a technique on the specified channel
        Args:
            channel (int): The number of the channel to load the technique onto
            technique (Technique): The technique to load
            first (bool): Whether this technique is the first technique
            last (bool): Thether this technique is the last technique
        Raises:
            ECLibError: On errors from the EClib communications library
        """
        if self.series == 'sp300':
            filename, ext = os.path.splitext(technique.technique_filename)
            c_technique_file = ctypes.create_string_buffer(filename + '4' + ext)
        else:
            c_technique_file = ctypes.create_string_buffer(
                technique.technique_filename
            )

        # Init TECCParams
        c_tecc_params = TECCParams()
        # Get the array of parameter structs
        c_params = technique.c_args(self)
        # Set the len
        c_tecc_params.len = len(c_params)  # pylint:disable=W0201
        p_params = ctypes.cast(c_params, ctypes.POINTER(TECCParam))
        c_tecc_params.pParams = p_params  # pylint:disable=W0201,C0103

        ret = self._eclib.BL_LoadTechnique(
            self._id,
            channel,
            ctypes.byref(c_technique_file),
            c_tecc_params,
            first,
            last,
            False,
        )
        self.check_eclib_return_code(ret)

    def define_bool_parameter(self, label, value, index, tecc_param):
        """Defines a boolean TECCParam for a technique
        This is a library convinience function to fill out the TECCParam struct
        in the correct way for a boolean value.
        Args:
            label (str): The label of the parameter
            value (bool): The boolean value for the parameter
            index (int): The index of the parameter
            tecc_param (TECCParam): An TECCParam struct
        """
        c_label = ctypes.create_string_buffer(label)
        ret = self._eclib.BL_DefineBoolParameter(
            ctypes.byref(c_label), value, index, ctypes.byref(tecc_param)
        )
        self.check_eclib_return_code(ret)

    def define_single_parameter(self, label, value, index, tecc_param):
        """Defines a single (float) TECCParam for a technique
        This is a library convinience function to fill out the TECCParam struct
        in the correct way for a single (float) value.
        Args:
            label (str): The label of the parameter
            value (float): The float value for the parameter
            index (int): The index of the parameter
            tecc_param (TECCParam): An TECCParam struct
        """
        c_label = ctypes.create_string_buffer(label)
        ret = self._eclib.BL_DefineSglParameter(
            ctypes.byref(c_label), ctypes.c_float(value), index, ctypes.byref(tecc_param),
        )
        self.check_eclib_return_code(ret)

    def define_integer_parameter(self, label, value, index, tecc_param):
        """Defines an integer TECCParam for a technique
        This is a library convinience function to fill out the TECCParam struct
        in the correct way for a integer value.
        Args:
            label (str): The label of the parameter
            value (int): The integer value for the parameter
            index (int): The index of the parameter
            tecc_param (TECCParam): An TECCParam struct
        """
        c_label = ctypes.create_string_buffer(label)
        ret = self._eclib.BL_DefineIntParameter(
            ctypes.byref(c_label), value, index, ctypes.byref(tecc_param)
        )
        self.check_eclib_return_code(ret)

    # Start/stop functions:
    def start_channel(self, channel):
        """Start the channel
        Args:
            channel (int): The channel number
        """
        ret = self._eclib.BL_StartChannel(self._id, channel)
        self.check_eclib_return_code(ret)

    def stop_channel(self, channel):
        """Stop the channel
        Args:
            channel (int): The channel number
        """
        ret = self._eclib.BL_StopChannel(self._id, channel)
        self.check_eclib_return_code(ret)

    # Data functions
    def get_current_values(self, channel):
        """Get the current values for the spcified channel
        Args:
            channel (int): The number of the channel (zero based)
        Returns:
            dict: A dict of current values information
        """
        current_values = CurrentValues()
        ret = self._eclib.BL_GetCurrentValues(
            self._id, channel, ctypes.byref(current_values)
        )
        self.check_eclib_return_code(ret)

        # Convert the struct to a dict and translate a few values
        out = ctypes.structure_to_dict(current_values)
        out['State(translated)'] = STATES[out['State']]
        out['IRange(translated)'] = I_RANGES[out['IRange']]
        return out

    def get_data(self, channel):
        """Get data for the specified channel
        Args:
            channel (int): The number of the channel (zero based)
        Returns:
            :class:`.KBIOData`: A :class:`.KBIOData` object or None if no data
                was available
        """
        # Raw data is retrieved in an array of integers
        c_databuffer = (ctypes.c_uint32 * 1000)()
        p_data_buffer = ctypes.cast(c_databuffer, ctypes.POINTER(ctypes.c_uint32))
        c_data_infos = DataInfos()
        c_current_values = CurrentValues()

        ret = self._eclib.BL_GetData(
            self._id,
            channel,
            p_data_buffer,
            ctypes.byref(c_data_infos),
            ctypes.byref(c_current_values),
        )
        self.check_eclib_return_code(ret)

        # The KBIOData will ask the appropriate techniques for which data
        # fields they return data in
        data = KBIOData(c_databuffer, c_data_infos, c_current_values, self)
        if data.technique == 'KBIO_TECHID_NONE':
            data = None

        return data

    def convert_numeric_into_single(self, numeric):
        """Convert a numeric (integer) into a float
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
            numeric (int): The integer that represents a float
        Returns:
            float: The float value
        """
        c_out_float = ctypes.c_float()
        ret = self._eclib.BL_ConvertNumericIntoSingle(
            numeric,
            ctypes.byref(c_out_float)
        )
        self.check_eclib_return_code(ret)
        return c_out_float.value

    def check_eclib_return_code(self, error_code):
        """Check a ECLib return code and raise the appropriate exception"""
        if error_code < 0:
            message = self.get_error_message(error_code)
            raise ECLibError(message, error_code)


class HCP1005(GeneralPotentiostat):
    """Specific driver for the HCCP-150 potentiostat"""

    def __init__(self, address, EClib_dll_path=None):
        """Initialize the SP150 potentiostat driver
        See the __init__ method for the GeneralPotentiostat class for an
        explanation of the arguments.
        """
        super(HCCP1005, self).__init__(
            type_='KBIO_DEV_HCP1005',
            address=address,
            EClib_dll_path=EClib_dll_path
        )


########## Auxillary classes
class KBIOData(object):
    """Class used to represent data obtained with a get_data call
    The data can be obtained as lists of floats through attributes on this
    class. The time is always available through the 'time' attribute. The
    attribute names for the rest of the data, are the same as their names as
    listed in the field_names attribute. E.g:
    * kbio_data.Ewe
    * kbio_data.I
    Provided that numpy is installed, the data can also be obtained as numpy
    arrays by appending '_numpy' to the attribute name. E.g:
    * kbio_data.Ewe.numpy
    * kbio_data.I_numpy
    """

    def __init__(self, c_databuffer, c_data_infos, c_current_values,
                 instrument):
        """Initialize the KBIOData object
        Args:
            c_databuffer (Array of :py:class:`ctypes.c_uint32`): ctypes array
                of c_uint32 used as the data buffer
            c_data_infos (:class:`.DataInfos`): Data information structure
            c_current_values (:class:`CurrentValues`): Current values structure
            instrument (:class:`GeneralPotentiostat`): Instrument instance,
                should be an instance of a subclass of
                :class:`GeneralPotentiostat`
        Raises:
            ECLibCustomException: Where the error codes indicate the following:
                * -20000 means that the technique has no entry in
                  :data:`TECHNIQUE_IDENTIFIERS_TO_CLASS`
                * -20001 means that the technique class has no ``data_fields``
                  class variable
                * -20002 means that the ``data_fields`` class variables of the
                  technique does not contain the right information
        """
        technique_id = c_data_infos.TechniqueID
        self.technique = TECHNIQUE_IDENTIFIERS[technique_id]

        # Technique 0 means no data, get_data checks for this, so just return
        if technique_id == 0:
            return

        # Extract the process index, used to seperate data field classes for
        # techniques that support that, self.process = 1 also means no_time
        # variable in the beginning
        self.process = c_data_infos.ProcessIndex
        # Init the data_fields
        self.data_fields = self._init_data_fields(instrument)

        # Extract the number of points and columns
        self.number_of_points = c_data_infos.NbRaws
        self.number_of_columns = c_data_infos.NbCols
        self.starttime = c_data_infos.StartTime

        # Init time property, if the measurement process index indicates that
        # it has a special time variable
        if self.process == 0:
            self.time = []

        # Make lists for the data in properties named after the field_names
        for data_field in self.data_fields:
            setattr(self, data_field.name, [])

        # Parse the data
        self._parse_data(c_databuffer, c_current_values.TimeBase,
                         instrument)

    def _init_data_fields(self, instrument):
        """Initialize the data fields property"""
        # Get the data_fields class variable from the corresponding technique
        # class
        if self.technique not in TECHNIQUE_IDENTIFIERS_TO_CLASS:
            message = \
                'The technique \'{}\' has no entry in '\
                'TECHNIQUE_IDENTIFIERS_TO_CLASS. The is required to be able '\
                'to interpret the data'.format(self.technique)
            raise ECLibCustomException(message, -20000)
        technique_class = TECHNIQUE_IDENTIFIERS_TO_CLASS[
            self.technique]

        if 'data_fields' not in technique_class.__dict__:
            message = 'The technique class {} does not defined a '\
                      '\'data_fields\' class variable, which is required for '\
                      'data interpretation.'.format(technique_class.__name__)
            raise ECLibCustomException(message, -20001)

        data_fields_complete = technique_class.data_fields
        if self.process == 1:  # Process 1 means no special time field
            try:
                data_fields_out = data_fields_complete['no_time']
            except KeyError:
                message = 'Unable to get data_fields from technique class. '\
                          'The data_fields class variable in the technique '\
                          'class must have either a \'no_time\' key when '\
                          'returning data with process index 1'
                raise ECLibCustomException(message, -20002)
        else:
            try:
                data_fields_out = data_fields_complete['common']
            except KeyError:
                try:
                    data_fields_out = data_fields_complete[
                        instrument.series]
                except KeyError:
                    message =\
                        'Unable to get data_fields from technique class. '\
                        'The data_fields class variable in the technique '\
                        'class must have either a \'common\' or a \'{}\' '\
                        'key'.format(instrument.series)
                    raise ECLibCustomException(message, -20002)

        return data_fields_out

    def _parse_data(self, c_databuffer, timebase, instrument):
        """Parse the data
        Args:
            timebase (float): The timebase for the time calculation
        See :meth:`.__init__` for information about remaining args
        """
        # The data is written as one long array of points with a certain
        # amount of colums. Get the index of the first item of each point by
        # getting the range from 0 til n_point * n_columns in jumps of
        # n_columns
        for index in range(
                0, self.number_of_points * self.number_of_columns,
                self.number_of_columns):
            # If there is a special time variable
            if self.process == 0:
                # Calculate the time
                t_high = c_databuffer[index]
                t_low = c_databuffer[index + 1]
                # NOTE: The documentation uses a bitshift operation for the:
                # ((t_high * 2 ** 32) + tlow) operation as
                # ((thigh << 32) + tlow), but I could not be bothered to
                # figure out exactly how a bitshift operation is defined for
                # an int class that can change internal representation, so I
                # just do the explicit multiplication
                self.time.append(
                    self.starttime +\
                    timebase * ((t_high * 2 ** 32) + t_low)
                )
                # Only offset reading the rest of the variables if there is a
                # special conversion time variable
                time_variable_offset = 2
            else:
                time_variable_offset = 0

            # Get remaining fields as defined in data fields
            for field_number, data_field in enumerate(
                    self.data_fields):
                value = c_databuffer[index + time_variable_offset +
                                     field_number]
                # If the type is supposed to be float, convert the numeric to
                # float using the convinience function
                if data_field.type is c_float:
                    value = instrument.convert_numeric_into_single(
                        value)

                # Append the field value to the appropriate list in a property
                getattr(self, data_field.name).append(value)

        # Check that the rest of the buffer is blank
        for index in range(
                self.number_of_points * self.number_of_columns, 1000):
            assert c_databuffer[index] == 0

    def __getattr__(self, key):
        """Return generated numpy arrays for the data instead of lists, if the
        requested property in on the form field_name + '_numpy'
        """
        # __getattr__ is only called after the check of whether the key is in
        # the instance dict, therefore it is ok to raise attribute error at
        # this points if the key does not have the special form we expect
        if key.endswith('_numpy'):
            # Get the requested field name e.g. Ewe
            requested_field = key.split('_numpy')[0]
            if requested_field in self.data_field_names or\
               requested_field == 'time':
                if GOT_NUMPY:
                    # Determin the numpy type to convert to
                    dtype = None
                    if requested_field == 'time':
                        dtype = float
                    else:
                        for field in self.data_fields:
                            if field.name == requested_field:
                                if field.type is c_float:
                                    dtype = float
                                elif field.type is c_uint32:
                                    dtype = int

                    if dtype is None:
                        message = 'Unable to infer the numpy data type for '\
                                  'requested field: {}'.format(requested_field)
                        raise ValueError(message)

                    # Convert the data and return the numpy array
                    return numpy.array(  # pylint: disable=no-member
                        getattr(self, requested_field),
                        dtype=dtype)
                else:
                    message = 'The numpy module is required to get the data '\
                              'as numpy arrays'
                    raise RuntimeError(message)

        message = '{} object has no attribute {}'.format(
            self.__class__, key)
        raise AttributeError(message)

    @property
    def data_field_names(self):
        """Return a list of extra data fields names (besides time)"""
        return [data_field.name for data_field in self.data_fields]
