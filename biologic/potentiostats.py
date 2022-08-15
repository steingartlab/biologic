import ctypes
import numpy as np
import os

import constants, exceptions, structures


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

    def __init__(
        self,
        type_: str,
        address: str,
        EClib_dll_path:
        str = 'C:\EC-Lab Development Package\EC-Lab Development Package\EClib64.dll',
        series: str = 'vmp3'
        ):
        """Initialize the potentiostat driver.

        Args:
            type_ (str): The device type e.g. 'KBIO_DEV_SP150'
            address (str): The address of the instrument, either IP address or
                USB0, USB1 etc
            EClib_dll_path (str): The path to the EClib DLL.
                Must be modified if using the 32-bit version.
                Defaults to 'C:\\EC-Lab Development Package\\EC-Lab Development Package\\EClib64.dll'
            series (str, optional): One of two series of instruments, either
                'sp300' or 'vmp3'. Defaults to 'vmp3'.
        
        Raises:
            WindowsError: If the EClib DLL cannot be found.
        """

        self._type = type_
        self.address = address
        self._eclib = ctypes.WinDLL(EClib_dll_path)
        self.series = series  # HCP-1005 is in this series (as opposed to SP-300)

        self._id = None
        self._device_info = None

    @property
    def id_number(self) -> int:
        """Return the device id as an int"""

        if self._id is None:
            return None

        return self._id.value

    @property
    def device_info(self) -> dict:
        """Return the device information.

        Returns:
            dict or None: The device information as a dict or None if the
                device is not connected.
        """

        if self._device_info is None:
            return None
        # out['DeviceCode(translated)'] = DEVICE_CODES[out['DeviceCode']]
        # 1: 'KBIO_DEV_VMP2',

        out = ctypes.structure_to_dict(self._device_info)
        out['DeviceCode(translated)'] = constants.Device[
            out['DeviceCode']]

        return out

    # # General functions
    # def get_lib_version(self):
    #     """Return the version of the EClib communications library.

    #     Returns:
    #         str: The version string for the library
    #     """

    #     size = ctypes.c_uint32(255)
    #     version = ctypes.create_string_buffer(255)
    #     ret = self._eclib.BL_GetLibVersion(ctypes.byref(version),
    #                                        ctypes.byref(size))
    #     self.check_eclib_return_code(ret)

    #     return version.value

    def get_error_message(self, error_code: int) -> str:
        """Return the error message corresponding to error_code.
        
        Args:
            error_code (int): The error number to translate.
        
        Returns:
            str: The error message corresponding to error_code.
        """

        message = ctypes.create_string_buffer(255)
        number_of_chars = ctypes.c_uint32(255)
        ret = self._eclib.BL_GetErrorMsg(
            error_code, ctypes.byref(message),
            ctypes.byref(number_of_chars)
            )
        # IMPORTANT, we cannot use, self.check_eclib_return_code here, since
        # that internally uses this method, thus we have the potential for an
        # infinite loop
        if ret < 0:
            err_msg = 'The error message is unknown, because it is the '\
                      'method to retrieve the error message with that fails. '\
                      'See the error codes sections (5.4) of the EC-Lab '\
                      'development package documentation to get the meaning '\
                      'of the error code.'
            raise exceptions.ECLibError(err_msg, ret)
        return message.value

    def connect(self, timeout: int = 5) -> dict:
        """Connect to the instrument and return the device info.
        
        Args:
            timeout (int): The connect timeout.
        
        Returns:
            dict or None: The device information as a dict or None if the
                device is not connected.
        
        Raises:
            ECLibCustomException: If this class does not match the device type.
        """

        # address = ctypes.create_string_buffer(len(self.address))
        address = ctypes.c_char_p(self.address.encode())
        self._id = ctypes.c_int32()
        device_info = structures.DeviceInfos()

        status = self._eclib.BL_Connect(
            ctypes.byref(address),
            timeout,
            ctypes.byref(self._id),
            ctypes.byref(device_info)
        )

        self.check_eclib_return_code(status)

        if constants.Device[device_info.DeviceCode] != self._type:
            message = f'The device type ({constants.Device[device_info.DeviceCode]})'\
                       'returned from the device on connect does not match the'\
                       'device type of the class ({self._type})'

            raise exceptions.ECLibCustomException(-9000, message)

        self._device_info = device_info

        return self.device_info

    def disconnect(self):
        """Disconnect from the device"""

        status = self._eclib.BL_Disconnect(self._id)

        self.check_eclib_return_code(status)

        self._id = None
        self._device_info = None

    def test_connection(self):
        """Test the connection"""

        ret = self._eclib.BL_TestConnection(self._id)

        self.check_eclib_return_code(ret)

    def load_firmware(
        self, channels: list, force_reload: bool = False
        ) -> list:
        """Load firmware on the specified channels, if not already loaded.

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
        p_results = ctypes.cast(
            c_results, ctypes.POINTER(ctypes.c_int32)
            )

        c_channels = (ctypes.c_uint8 * len(channels))()

        for index in range(len(channels)):
            c_channels[index] = channels[index]

        p_channels = ctypes.cast(
            c_channels, ctypes.POINTER(ctypes.c_uint8)
            )

        status = self._eclib.BL_LoadFirmware(
            self._id, p_channels, p_results, len(channels), False,
            force_reload, None, None
            )

        self.check_eclib_return_code(status)

        return list(c_results)

    def is_channel_plugged(self, channel) -> bool:
        """Test if the selected channel is plugged.

        Args:
            channel (int): Selected channel (0-15 on most devices).
        
        Returns:
            bool: Whether the channel is plugged.
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

        status = self._eclib.BL_GetChannelsPlugged(
            self._id, pstatus, 16
            )

        self.check_eclib_return_code(status)

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

        channel_info = structures.ChannelInfos()
        self._eclib.BL_GetChannelInfos(
            self._id, channel, ctypes.byref(channel_info)
            )
        out = ctypes.structure_to_dict(channel_info)

        # Translate code to strings
        out['FirmwareCode(translated)'] = \
            constants.Firmware[out['FirmwareCode']]
        out['AmpCode(translated)'] = constants.Amplifier.get(
            out['AmpCode']
            )
        out['State(translated)'] = constants.State.get(out['State'])
        out['MaxIRange(translated)'] = constants.CurrentRange.get(
            out['MaxIRange']
            )
        out['MinIRange(translated)'] = constants.CurrentRange.get(
            out['MinIRange']
            )
        out['MaxBandwidth'] = constants.Bandwidth.get(
            out['MaxBandwidth']
            )

        return out

    def get_message(self, channel):
        """Return a message from the firmware of a channel """

        size = ctypes.c_uint32(255)
        message = ctypes.create_string_buffer(255)

        status = self._eclib.BL_GetMessage(
            self._id, channel, ctypes.byref(message),
            ctypes.byref(size)
            )

        self.check_eclib_return_code(status)

        return message.value

    # Technique functions:
    def load_technique(
        self, channel, technique, first=True, last=True
        ):
        """Load a technique on the specified channel
        
        Args:
            channel (int): The number of the channel to load the technique onto.
            technique (Technique): The technique to load.
            first (bool): Whether this technique is the first technique.
            last (bool): Thether this technique is the last technique.
        
        Raises:
            ECLibError: On errors from the EClib communications library.
        """

        c_technique_file = ctypes.create_string_buffer(
            technique.technique_filename
            )

        # Init TECCParams
        c_tecc_params = structures.TECCParams()
        # Get the array of parameter structs
        c_params = technique.c_args(self)
        # Set the len
        c_tecc_params.len = len(c_params)  # pylint:disable=W0201
        p_params = ctypes.cast(
            c_params, ctypes.POINTER(structures.TECCParam)
            )
        c_tecc_params.pParams = p_params  # pylint:disable=W0201,C0103

        status = self._eclib.BL_LoadTechnique(
            self._id,
            channel,
            ctypes.byref(c_technique_file),
            c_tecc_params,
            first,
            last,
            False,
            )

        self.check_eclib_return_code(status)

    def define_bool_parameter(self, label, value, index, tecc_param):
        """Defines a boolean TECCParam for a technique.

        This is a library convinience function to fill out the TECCParam struct
        for a boolean value.
        
        Args:
            label (str): The label of the parameter
            value (bool): The boolean value for the parameter
            index (int): The index of the parameter
            tecc_param (TECCParam): An TECCParam struct
        """

        c_label = ctypes.create_string_buffer(label)
        status = self._eclib.BL_DefineBoolParameter(
            ctypes.byref(c_label), value, index,
            ctypes.byref(tecc_param)
            )

        self.check_eclib_return_code(status)

    def define_single_parameter(
        self, label, value, index, tecc_param
        ):
        """Defines a single (float) TECCParam for a technique
        This is a library convenience function to corectly fill
        out the TECCParam struct for a single (float) value.

        Args:
            label (str): The label of the parameter
            value (float): The float value for the parameter
            index (int): The index of the parameter
            tecc_param (TECCParam): An TECCParam struct
        """

        c_label = ctypes.create_string_buffer(label)

        status = self._eclib.BL_DefineSglParameter(
            ctypes.byref(c_label),
            ctypes.c_float(value),
            index,
            ctypes.byref(tecc_param),
            )

        self.check_eclib_return_code(status)

    def define_integer_parameter(
        self, label: str, value: int, index: int,
        tecc_param: structures.TECCParam
        ):
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

        status = self._eclib.BL_DefineIntParameter(
            ctypes.byref(c_label), value, index,
            ctypes.byref(tecc_param)
            )

        self.check_eclib_return_code(status)

    # Start/stop functions:
    def start_channel(self, channel):
        """Start the channel
        Args:
            channel (int): The channel number
        """

        status = self._eclib.BL_StartChannel(self._id, channel)

        self.check_eclib_return_code(status)

    def stop_channel(self, channel):
        """Stop the channel
        Args:
            channel (int): The channel number
        """

        status = self._eclib.BL_StopChannel(self._id, channel)

        self.check_eclib_return_code(status)

    def get_current_values(self, channel):
        """Get the current values for the spcified channel
        
        Args:
            channel (int): The number of the channel (zero based)
        
        Returns:
            dict: A dict of current values information
        """

        current_values = structures.CurrentValues()

        status = self._eclib.BL_GetCurrentValues(
            self._id, channel, ctypes.byref(current_values)
            )

        self.check_eclib_return_code(status)

        # Convert the struct to a dict and translate a few values
        out = ctypes.structure_to_dict(current_values)
        out['State(translated)'] = constants.State[out['State']]
        out['IRange(translated)'] = constants.CurrentRange[
            out['IRange']]

        return out

    def get_data(self, channel):
        """Get data for the specified channel.
        
        Args:
            channel (int): The number of the channel (zero based)
        
        Returns:
            :class:`.KBIOData`: A :class:`.KBIOData` object or None if no data
                was available
        """

        # Raw data is retrieved in an array of integers
        c_databuffer = (ctypes.c_uint32 * 1000)()
        p_data_buffer = ctypes.cast(
            c_databuffer, ctypes.POINTER(ctypes.c_uint32)
            )
        c_data_infos = structures.DataInfos()
        c_current_values = structures.CurrentValues()

        status = self._eclib.BL_GetData(
            self._id,
            channel,
            p_data_buffer,
            ctypes.byref(c_data_infos),
            ctypes.byref(c_current_values),
            )
        self.check_eclib_return_code(status)

        # The KBIOData will ask the appropriate techniques for which data
        # fields they return data in
        data = KBIOData(
            c_databuffer, c_data_infos, c_current_values, self
            )

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

        status = self._eclib.BL_ConvertNumericIntoSingle(
            numeric, ctypes.byref(c_out_float)
            )

        self.check_eclib_return_code(status)

        return c_out_float.value

    def check_eclib_return_code(self, error_code):
        """Check a ECLib return code and raise the appropriate exception"""

        if error_code < 0:
            message = self.get_error_message(error_code)
            print(message)
            raise exceptions.ECLibError(message, error_code)


class SP150(GeneralPotentiostat):
    """Specific driver for the SP-150 potentiostat"""

    def __init__(self, address):
        """Initialize the SP150 potentiostat driver
        See the __init__ method for the GeneralPotentiostat class for an
        explanation of the arguments.
        """

        super(SP150, self).__init__(
            type_='KBIO_DEV_SP150',
            address=address
        )


class HCP1005(GeneralPotentiostat):
    """Specific driver for the HCP-1005 potentiostat"""

    def __init__(self, address):
        """Initialize the HCP-1005 potentiostat driver
        See the __init__ method for the GeneralPotentiostat class for an
        explanation of the arguments.
        """

        super(HCP1005, self).__init__(
            type_='KBIO_DEV_HCP1005',
            address=address
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
    """

    def __init__(
        self, c_databuffer, c_data_infos, c_current_values, instrument
        ):
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
                  :data:`constants.Technique_TO_CLASS`
                * -20001 means that the technique class has no ``data_fields``
                  class variable
                * -20002 means that the ``data_fields`` class variables of the
                  technique does not contain the right information
        """

        technique_id = c_data_infos.TechniqueID
        self.technique = constants.Technique[technique_id]

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
        self._parse_data(
            c_databuffer, c_current_values.TimeBase, instrument
            )

    def _init_data_fields(self, instrument):
        """Initialize the data fields property"""
        # Get the data_fields class variable from the corresponding technique
        # class
        if self.technique not in constants.Technique:
            message = \
                f'The technique \'{self.technique}\' has no entry in '\
                'constants.Technique_TO_CLASS. The is required to be able '\
                'to interpret the data'

            raise exceptions.ECLibCustomException(message, -20000)

        technique_class = constants.Technique[self.technique]

        if 'data_fields' not in technique_class.__dict__:
            message = 'The technique class {} does not defined a '\
                      '\'data_fields\' class variable, which is required for '\
                      'data interpretation.'.format(technique_class.__name__)
            raise exceptions.ECLibCustomException(message, -20001)

        data_fields_complete = technique_class.data_fields

        # if self.process != 1:
        #     try:
        #         data_fields_out = data_fields_complete['common']
        #     except KeyError:
        #         try:
        #             data_fields_out = data_fields_complete[
        #                 instrument.series]
        #         except KeyError:
        #             message =\
        #                 'Unable to get data_fields from technique class. '\
        #                 'The data_fields class variable in the technique '\
        #                 'class must have either a \'common\' or a \'{}\' '\
        #                 'key'.format(instrument.series)
        #             raise exceptions.ECLibCustomException(
        #                 message, -20002
        #                 )


        if self.process == 1:  # Process 1 means no special time field
            try:
                data_fields_out = data_fields_complete['no_time']
            except KeyError:
                message = 'Unable to get data_fields from technique class. '\
                          'The data_fields class variable in the technique '\
                          'class must have either a \'no_time\' key when '\
                          'returning data with process index 1'
                raise exceptions.ECLibCustomException(message, -20002)
        else:
            try:
                data_fields_out = data_fields_complete['common']
            except KeyError:
                try:
                    data_fields_out = data_fields_complete[
                        instrument.series]
                except KeyError:
                    message =\
                        f'Unable to get data_fields from technique class. '\
                        'The data_fields class variable in the technique '\
                        'class must have either a \'common\' or a \'{instrument.series}\' '\
                        'key'
                    raise exceptions.ECLibCustomException(
                        message, -20002
                        )

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
            self.number_of_columns
            ):
            # If there is not a special time variable
            if self.process != 0:
                time_variable_offset = 0
                continue

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

            # Get remaining fields as defined in data fields
            for field_number, data_field in enumerate(
                self.data_fields
                ):
                value = c_databuffer[index + time_variable_offset +
                                     field_number]
                # If the type is supposed to be float, convert the numeric to
                # float using the convinience function
                if data_field.type is ctypes.c_float:
                    value = instrument.convert_numeric_into_single(
                        value
                        )

                # Append the field value to the appropriate list in a property
                getattr(self, data_field.name).append(value)

        # Check that the rest of the buffer is blank
        for index in range(
            self.number_of_points * self.number_of_columns, 1000
            ):
            assert c_databuffer[index] == 0

    @property
    def data_field_names(self):
        """Return a list of extra data fields names (besides time)"""

        return [data_field.name for data_field in self.data_fields]
