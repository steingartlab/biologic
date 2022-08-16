import ctypes
import json

from biologic import constants, exceptions, handler, structures

with open('biologic/config.json') as f:
    settings = json.load(f)

driverpath = settings['driver']['driverpath']


class InstrumentFinder:
    """Finds BioLogic instruments connected via ethernet.
    
    Attributes:
        self.driver (ctypes.WinDLL): Driver for calling EC-Lab functions.
    """

    def __init__(self, driver: str = 'blfind64.dll'):
        """
        Args:
            driver (str, optional): Driver filename. For distinguishing
                between 32 and 64-bit systems. Defaults to 'blfind64.dll'.
        """
        self.driver = ctypes.WinDLL(driverpath + driver)

    def find(self, bytes_: int = 255) -> str:
        """Returns IP-addresses of connected BioLogic potentiostats.

        Args:
            bytes_ (int, optional): Number of bytes to allocate to buffer.
                Defaults to 255.

        Returns:
            str or None: IP-address of connected potentiostats.
                If none are found it returns None.
        """

        lst_dev = ctypes.create_string_buffer(bytes_)
        size = ctypes.c_uint32(bytes_)
        nbr_dev = ctypes.c_uint32(bytes_)

        status = self.driver.BL_FindEChemEthDev(
            ctypes.byref(lst_dev), ctypes.byref(size),
            ctypes.byref(nbr_dev)
            )

        assert_status_ok(driver=self.driver, return_code=status)

        ip = parse_potentiostat_search(bytes_string=lst_dev)

        return ip


class GeneralPotentiostat(object):
    """Baseclass for interacting with potentiostats controllable by EC-lib DLL.

    Drivers for specific potentiostat types will inherit from this class.

    Raises:
        ECLibError: All regular methods in this class use the EC-lib DLL
            communications library to talk with the equipment and they will
            raise this exception if this library reports an error. It will not
            be explicitly mentioned in every single method.
    """

    def __init__(
        self,
        type_: str,
        driver: str = 'EClib64.dll',
        series: str = 'vmp3'
        ):
        """Initialize the potentiostat driver.

        Args:
            type_ (str): Device type, e.g. 'KBIO_DEV_HCP1005'.
            EClib_dll_path (str): Driver filename. For distinguishing
                between 32 and 64-bit systems. Defaults to 'EClib64.dll'.
            series (str, optional): One of two series of instruments, either
                'sp300' or 'vmp3'. Defaults to 'vmp3'.
        
        Raises:
            WindowsError: If driver isn't found.
        """

        self._type = type_
        self.driver = ctypes.WinDLL(driverpath + driver)
        self.series = series

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

    def connect(self, ip_address, timeout: int = 5) -> dict:
        """Connects to instrument and returns device info.
        
        Args:
            timeout (int, optional): Wait for timeout number of seconds
                before timing out. Defaults to 5.
        
        Returns:dc
            dict or None: The device information as a dict or None if the
                device is not connected.
        
        Raises:
            ECLibCustomException: If this class does not match the device type.
        """

        address = ctypes.create_string_buffer(ip_address.encode())
        self._id = ctypes.c_int32()
        device_info = structures.DeviceInfos()

        status = self.driver.BL_Connect(
            ctypes.byref(address),
            ctypes.c_uint8(timeout),
            ctypes.byref(self._id),
            ctypes.byref(device_info)
            )   

        assert_status_ok(driver=self.driver, return_code=status)

        # assert_device_type_ok(
        #     device_code=device_info.DeviceCode,
        #     reference_device=self._type
        #     )

        # self._device_info = device_info

        # return self.device_info

    def disconnect(self):
        """Disconnect from the device"""

        status = self.driver.BL_Disconnect(self._id)

        assert_status_ok(driver=self.driver, return_code=status)

        self._id = None
        self._device_info = None

    def test_connection(self):
        """Test the connection"""

        status = self.driver.BL_TestConnection(self._id)

        assert_status_ok(status)


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

        status = self.driver.BL_LoadFirmware(
            self._id,
            p_channels,
            p_results,
            len(channels),
            False,
            force_reload,
            None,
            None
        )

        assert_status_ok(driver=self.driver, return_code=status)

        return list(c_results)

    def is_channel_plugged(self, channel) -> bool:
        """Test if the selected channel is plugged.

        Args:
            channel (int): Selected channel (0-15 on most devices).
        
        Returns:
            bool: Whether the channel is plugged.
        """

        result = self.driver.BL_IsChannelPlugged(self._id, channel)

        return result == 1

    def get_channels_plugged(self):
        """Get information about which channels are plugged.

        Returns:
            (list): A list of channel plugged statusses as booleans
        """

        status = (ctypes.c_uint8 * 16)()
        pstatus = ctypes.cast(status, ctypes.POINTER(ctypes.c_uint8))

        status = self.driver.BL_GetChannelsPlugged(
            self._id, pstatus, 16
            )

        assert_status_ok(driver=self.driver, return_code=status)

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
        self.driver.BL_GetChannelInfos(
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

        status = self.driver.BL_GetMessage(
            self._id, channel, ctypes.byref(message),
            ctypes.byref(size)
            )

        assert_status_ok(driver=self.driver, return_code=status)

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

        status = self.driver.BL_LoadTechnique(
            self._id,
            channel,
            ctypes.byref(c_technique_file),
            c_tecc_params,
            first,
            last,
            False,
            )

        assert_status_ok(driver=self.driver, return_code=status)

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
        status = self.driver.BL_DefineBoolParameter(
            ctypes.byref(c_label), value, index,
            ctypes.byref(tecc_param)
            )

        assert_status_ok(driver=self.driver, return_code=status)

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

        status = self.driver.BL_DefineSglParameter(
            ctypes.byref(c_label),
            ctypes.c_float(value),
            index,
            ctypes.byref(tecc_param),
            )

        assert_status_ok(driver=self.driver, return_code=status)

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

        status = self.driver.BL_DefineIntParameter(
            ctypes.byref(c_label), value, index,
            ctypes.byref(tecc_param)
            )

        assert_status_ok(driver=self.driver, return_code=status)

    # Start/stop functions:
    def start_channel(self, channel):
        """Start the channel
        Args:
            channel (int): The channel number
        """

        status = self.driver.BL_StartChannel(self._id, channel)

        assert_status_ok(driver=self.driver, return_code=status)

    def stop_channel(self, channel):
        """Stop the channel
        Args:
            channel (int): The channel number
        """

        status = self.driver.BL_StopChannel(self._id, channel)

        assert_status_ok(driver=self.driver, return_code=status)

    def get_current_values(self, channel):
        """Get the current values for the spcified channel
        
        Args:
            channel (int): The number of the channel (zero based)
        
        Returns:
            dict: A dict of current values information
        """

        current_values = structures.CurrentValues()

        status = self.driver.BL_GetCurrentValues(
            self._id, channel, ctypes.byref(current_values)
            )

        assert_status_ok(driver=self.driver, return_code=status)

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

        status = self.driver.BL_GetData(
            self._id,
            channel,
            p_data_buffer,
            ctypes.byref(c_data_infos),
            ctypes.byref(c_current_values),
            )
        assert_status_ok(driver=self.driver, return_code=status)

        # The KBIOData will ask the appropriate techniques for which data
        # fields they return data in
        data = handler.KBIOData(
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

        status = self.driver.BL_ConvertNumericIntoSingle(
            numeric, ctypes.byref(c_out_float)
            )

        assert_status_ok(driver=self.driver, return_code=status)

        return c_out_float.value


class HCP1005(GeneralPotentiostat):
    """Specific driver for the HCP-1005 potentiostat"""

    def __init__(self):
        """Initialize the HCP-1005 potentiostat driver.
        Refer to superclass initializer for arguments.
        """

        super(HCP1005, self).__init__(
            type_='KBIO_DEV_HCP1005'
            )


def assert_device_type_ok(
    device_code: structures.DeviceInfos, reference_device: str
    ) -> None:
    """Checks whether returned device code is the expected device.

    Args:
        device_code (_type_): _description_
        reference_device (_type_): _description_

    Raises:
        exceptions.ECLibCustomException: If expected and actual
            don't match.
    """

    if constants.Device[device_code] == reference_device:
        return

    message = f'Device type ({constants.Device[device_code]})'\
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


def parse_potentiostat_search(bytes_string: bytes) -> str:
    """Extracts IP-address from potentiostat search.

    Hacky. Might fix later. Can only handle one device.

    Args:
        bytes_string (bytes): Result of BL_FindEChemEthDev()

    Returns:
        str: IP-address of connected potentiostat.
    """
    parsed = bytes_string.raw.decode()

    ip_w_unicode = parsed.split('$')[1]

    # Still contains unicode stuff. Got to remove
    ip = ''
    for character in ip_w_unicode:
        if character.encode('utf-8') == b'\x00':
            continue

        ip += character

    return ip