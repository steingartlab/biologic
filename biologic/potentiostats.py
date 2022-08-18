import ctypes
import json

from biologic import constants, exceptions, handler, structures, techniques

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

        ip_address = parse_potentiostat_search(bytes_string=lst_dev)

        return ip_address


class GeneralPotentiostat:
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
        """Retrieve device id as int."""

        if self._id is None:
            return None

        return self._id.value

    @property
    def device_info(self) -> dict:
        """Retrieve device information.

        Returns:
            dict or None: The device information as a dict or None if the
                device is not connected.
        """

        if self._device_info is None:
            return None

        out = structure_to_dict(self._device_info)
        out['DeviceCode(translated)'] = constants.Device(
            out['DeviceCode']
            ).value

        return out

    def connect(self, ip_address: str, timeout: int = 5) -> None:
        """Connects to instrument and returns device info.
        
        Args:
            ip_address (str): IP-address of device, e.g. from
                InstrumentFinder.find().
            timeout (int, optional): Wait for timeout number of seconds
                before timing out. Defaults to 5.
        
        Raises:
            ECLibCustomException: If class instance doesn't match device type.
        """

        address = ctypes.create_string_buffer(ip_address.encode())
        self._id = ctypes.c_int32()
        self._device_info = structures.DeviceInfos()

        status = self.driver.BL_Connect(
            ctypes.byref(address), ctypes.c_uint8(timeout),
            ctypes.byref(self._id), ctypes.byref(self._device_info)
            )

        assert_status_ok(driver=self.driver, return_code=status)

        assert_device_type_ok(
            device_code=self._device_info.DeviceCode,
            reference_device=self._type
            )

    def get_error_status(self, channel: int = 0, bytes_: int = 255):

        c_error_status = ctypes.create_string_buffer(bytes_)
        c_opt_pos = ctypes.create_string_buffer(bytes_)

        status = self.driver.BL_GetOptErr(
            self._id, channel, ctypes.byref(c_error_status),
            ctypes.byref(c_opt_pos)
            )

        assert_status_ok(driver=self.driver, return_code=status)

    def test_connection(self) -> None:
        """Tests device connection."""

        status = self.driver.BL_TestConnection(self._id)

        assert_status_ok(driver=self.driver, return_code=status)

    def disconnect(self) -> None:
        """Disconnects from device."""

        status = self.driver.BL_Disconnect(self._id)

        assert_status_ok(driver=self.driver, return_code=status)

        self._id = None
        self._device_info = None

    def load_firmware(
        self,
        channels: list,
        force_reload: bool = False,
        show_gauge: bool = True,
        kernel: str = 'kernel.bin',
        xlx: str = 'Vmp_ii_0437_a6.xlx'
        ) -> list:
        """Loads firmware on the specified channels.

        Args:
            channels (list): Boolean list with one entry per channel,
                specifying which channel the firmware should be loaded on.
                NOTE: The length of the list must correspond to the number
                of channels supported by the equipment, not the number of
                channels installed.
            force_reload (bool, optional): If True the firmware is forcefully
                reloaded. Defaults to False.
            show_gauge (bool, optional): If True a gauge is shown during the
                firmware loading. Defaults to False.

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

        bin_file: str = driverpath + kernel
        c_bin_file = ctypes.create_string_buffer(bin_file.encode())

        xlx_file: str = driverpath + xlx
        c_xlx_file = ctypes.create_string_buffer(xlx_file.encode())

        status = self.driver.BL_LoadFirmware(
            self._id, p_channels, p_results, len(channels),
            show_gauge, force_reload, ctypes.byref(c_bin_file),
            ctypes.byref(c_xlx_file)
            )

        assert_status_ok(driver=self.driver, return_code=status)

        return list(c_results)

    def get_channels_plugged(self, no_channels: int = 1) -> list:
        """Get information about which channels are plugged.

        Returns:
            (list): A boolean list of channels plugged.
        """

        status_ = (ctypes.c_uint8 * no_channels)()
        pstatus = ctypes.cast(status_, ctypes.POINTER(ctypes.c_uint8))

        status = self.driver.BL_GetChannelsPlugged(
            self._id, pstatus, no_channels
            )

        assert_status_ok(driver=self.driver, return_code=status)
        print([result == 1 for result in status_])
        return [result == 1 for result in status_]

    def is_channel_plugged(self, channel: int = 0) -> bool:
        """Test if the selected channel is plugged.

        Args:
            channel (int, optional): Selected channel.
                Defaults to 0.
        
        Returns:
            bool: Whether the channel is plugged or not.
        """

        result = self.driver.BL_IsChannelPlugged(self._id, channel)

        return bool(result)

    def get_channel_info(self, channel: int = 0) -> dict:
        """Get information about the specified channel.

        Args:
            channel (int, optional): Selected channel.
                Defaults to 0.   

        Returns:
            dict: Channel infos dict. The dict is created by conversion from
                :class:`.ChannelInfos` class (type
                :py:class:`ctypes.Structure`). See the documentation for that
                class for a list of available dict items. Besides the items
                listed, there are extra items for all the original items whose
                value can be converted from an integer code to a string. The
                keys for those values are suffixed by (translated).
        """

        c_channel_info = structures.ChannelInfos()
        self.driver.BL_GetChannelInfos(
            self._id, channel, ctypes.byref(c_channel_info)
            )
        channel_info = structure_to_dict(structure=c_channel_info)

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
        channel_info['MaxIRange(translated)'
                    ] = constants.CurrentRange(
                        channel_info['MaxIRange']
                        ).name
        channel_info['MinIRange(translated)'
                    ] = constants.CurrentRange(
                        channel_info['MinIRange']
                        ).name
        channel_info['MaxBandwidth'] = constants.Bandwidth(
            channel_info['MaxBandwidth']
            ).name

        for key, val in channel_info.items():
            print(f'{key}: {val}')

        return channel_info

    def get_message(self, channel: int = 0) -> str:
        """Return a message from the firmware of a channel.
        
        Args:
            channel (int, optional): Selected channel.
                Defaults to 0.
        
        Returns:
            str: Board description.
        """

        size = ctypes.c_uint32(255)
        message = ctypes.create_string_buffer(255)

        status = self.driver.BL_GetMessage(
            self._id, channel, ctypes.byref(message),
            ctypes.byref(size)
            )

        assert_status_ok(driver=self.driver, return_code=status)

        return message.value.decode()

    # Technique functions:
    def load_technique(
        self,
        technique: techniques.Technique,
        first: bool = True,
        last: bool = True,
        channel: int = 0
        ) -> None:
        """Load a technique onto the specified channel.
        
        Args:
            technique (techniques.Technique): The technique to load.
            first (bool, optional): Whether this technique is the first technique.
                Defaults to True.
            last (bool, optional): Thether this technique is the last technique.
                Defaults to True.
            channel (int, optional): Selected channel.
                Defaults to 0.

        Raises:
            ECLibError: On errors from the EClib communications library.
        """

        c_technique_file = ctypes.create_string_buffer(
            'C:\\Users\\stein\\github\\biologic\\EC-Lab Development Package\\EC-Lab Development Package\\ocv.ecc'
            .encode()
            )
        c_params = technique.c_args(self)
        c_tecc_params = structures.TEccParams()
        c_tecc_params.len = len(c_params)
        c_tecc_params.pParams = ctypes.cast(
            c_params, ctypes.POINTER(structures.TEccParam)
            )

        status = self.driver.BL_LoadTechnique(
            self._id,
            ctypes.c_uint8(channel),
            ctypes.byref(c_technique_file),
            c_tecc_params,
            ctypes.c_bool(first),
            ctypes.c_bool(last),
            ctypes.c_bool(False),
            )
        print(c_technique_file.raw.decode())

        assert_status_ok(driver=self.driver, return_code=status)

    def define_bool_parameter(
        self, label: str, value: bool, index: int,
        tecc_param: structures.TEccParam
        ) -> None:
        """Defines a boolean TECCParam for a technique.

        This is a library convenience function to fill
        out the TECCParam struct for a _boolean_ value.
        
        Args:
            label (str): Parameter label.
            value (bool): Parameter boolean value.
            index (int): Parameter index.
            tecc_param (TECCParam): A TECCParam struct.
        """

        c_label = ctypes.create_string_buffer(label.encode())

        status = self.driver.BL_DefineBoolParameter(
            ctypes.byref(c_label), value, index,
            ctypes.byref(tecc_param)
            )

        assert_status_ok(driver=self.driver, return_code=status)

    def define_single_parameter(
        self, label: str, value: bool, index: int,
        tecc_param: structures.TEccParam
        ) -> None:
        """Defines a single (float) TECCParam for a technique.

        This is a library convenience function to corectly fill
        out the TECCParam struct for a _single_ (float) value.

        Args:
            label (str): Parameter label.
            value (bool): Parameter boolean value.
            index (int): Parameter index.
            tecc_param (TECCParam): A TECCParam struct.
        """

        c_label = ctypes.create_string_buffer(label.encode())

        status = self.driver.BL_DefineSglParameter(
            ctypes.byref(c_label),
            ctypes.c_float(value),
            index,
            ctypes.byref(tecc_param),
            )

        assert_status_ok(driver=self.driver, return_code=status)

    def define_integer_parameter(
        self, label: str, value: int, index: int,
        tecc_param: structures.TEccParam
        ) -> None:
        """Defines an integer TECCParam for a technique.
        
        This is a library convinience function to fill
        out the TECCParam struct for an _integer_ value.

        Args:
            label (str): Parameter label.
            value (bool): Parameter boolean value.
            index (int): Parameter index.
            tecc_param (TECCParam): A TECCParam struct.
        """

        c_label = ctypes.create_string_buffer(label.encode())

        status = self.driver.BL_DefineIntParameter(
            ctypes.byref(c_label), value, index,
            ctypes.byref(tecc_param)
            )

        assert_status_ok(driver=self.driver, return_code=status)

    # Start/stop functions:
    def start_channel(self, channel: int = 0) -> None:
        """Start technique loaded on channel.
        
        Args:
            channel (int, optional): Selected channel.
                    Defaults to 0.
        """

        status = self.driver.BL_StartChannel(self._id, channel)

        assert_status_ok(driver=self.driver, return_code=status)

    def stop_channel(self, channel: int = 0) -> None:
        """Stop technique loaded on channel.

        Args:
            channel (int, optional): Selected channel.
                    Defaults to 0.
        """

        status = self.driver.BL_StopChannel(self._id, channel)

        assert_status_ok(driver=self.driver, return_code=status)

    def get_current_values(self, channel: int = 0) -> dict:
        """Get the current values for the spcified channel.
        
        Args:
            channel (int, optional): Selected channel.
                    Defaults to 0.
        
        Returns:
            dict: A dict of current values information
        """

        c_current_values = structures.CurrentValues()

        status = self.driver.BL_GetCurrentValues(
            self._id, channel, ctypes.byref(c_current_values)
            )

        assert_status_ok(driver=self.driver, return_code=status)

        # Convert the struct to a dict and translate a few values
        current_values = ctypes.structure_to_dict(c_current_values)
        current_values['State(translated)'] = constants.State(current_values['State']).name
        current_values['IRange(translated)'] = constants.CurrentRange(
            current_values['IRange']
            ).name

        return current_values

    def get_data(self, channel: int = 0) -> handler.KBIOData:
        """Get data for the specified channel.
        
        Args:
            channel (int, optional): Selected channel.
                    Defaults to 0.
        
        Returns:
            handler.KBIOData: Class instance (or None if none available.)
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

    def convert_numeric_to_single(self, numeric: int) -> float:
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

        super(HCP1005, self).__init__(type_='KBIO_DEV_HCP1005')


def structure_to_dict(structure: ctypes.Structure) -> dict:
    """Convert a ctypes.Structure to a python dict."""

    out = {}

    for key, _ in structure._fields_:
        out[key] = getattr(structure, key)

    return out


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