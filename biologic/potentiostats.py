"""Classes containing methods for using EC-Lab drivers to communicate with BioLogic potentiostat."""

import ctypes
import json
import typing

from biologic import constants, handler, structures, utils

with open('biologic/config.json') as f:
    settings = json.load(f)

driverpath = settings['driver']['driverpath']

driver = ctypes.WinDLL(driverpath + 'EClib64.dll')


class InstrumentFinder:
    """Finds BioLogic instruments connected via ethernet.
    
    Attributes:
        driver (ctypes.WinDLL): Driver for calling EC-Lab functions.
        self.ip_address (str): Instrument IP-address, e.g. '192.168.0.1'.
        self.instrument_type (str): Instrument type, e.g. 'SP-150'.
    """

    def __init__(self, driver: str = 'blfind64.dll'):
        """
        Args:
            driver (str, optional): Driver filename. For distinguishing
                between 32 and 64-bit systems. Defaults to 'blfind64.dll'.
        """
        self.driver = ctypes.WinDLL(driverpath + driver)
        self._ip_address: str = None
        self._instrument_type: str = None

    @property
    def ip_address(self) -> str:
        """Returns parsed IP-address of connected instrument.

        Returns:
            str: Instrument IP-address, e.g. '192.168.0.1'.
        """
        return self._ip_address

    @property
    def instrument_type(self) -> str:
        """Returns parsed type of connected instrument.

        Returns:
            str: Instrument type, e.g. 'SP-150'.
        """
        return self._instrument_type

    def find(self, bytes_: int = 255) -> None:
        """Searches for ethernet-connected BioLogic potentiostats.

        Args:
            bytes_ (int, optional): Number of bytes to allocate to buffer.
                Defaults to 255.
        """

        lst_dev = ctypes.create_string_buffer(bytes_)
        size = ctypes.c_uint32(bytes_)
        nbr_dev = ctypes.c_uint32(bytes_)

        status = self.driver.BL_FindEChemEthDev(
            ctypes.byref(lst_dev), ctypes.byref(size),
            ctypes.byref(nbr_dev)
            )

        utils.assert_status_ok(driver=driver, return_code=status)

        self._ip_address, self._instrument_type = utils.parse_potentiostat_search(
            bytes_string=lst_dev
            )


class GeneralPotentiostat:
    """Baseclass for interacting with potentiostats controllable by EC-lib DLL.

    Drivers for specific potentiostat types will inherit from this class.

    Raises:
        ECLibError: All regular methods in this class use the EC-lib DLL
            communications library to talk with the equipment and they will
            raise this exception if this library reports an error. It will not
            be explicitly mentioned in every single method.
    """

    def __init__(self, type_: str):
        """Initialize the potentiostat driver.

        Args:
            type_ (str): Device type, e.g. 'KBIO_DEV_HCP1005'.
        
        Raises:
            WindowsError: If driver isn't found.
        """

        self._type = type_

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

        out = utils.structure_to_dict(self._device_info)
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

        status = driver.BL_Connect(
            ctypes.byref(address), ctypes.c_uint8(timeout),
            ctypes.byref(self._id), ctypes.byref(self._device_info)
            )

        utils.assert_status_ok(driver=driver, return_code=status)

        utils.assert_device_type_ok(
            device_code=self._device_info.DeviceCode,
            reference_device=self._type
            )

    def get_error_status(self, channel: int = 0):

        c_opt_error = ctypes.c_int32()
        c_opt_pos = ctypes.c_int32()

        status = driver.BL_GetOptErr(
            self._id, channel, ctypes.byref(c_opt_error),
            ctypes.byref(c_opt_pos)
            )

        utils.assert_status_ok(driver=driver, return_code=status)

        print(
            'opterror:', c_opt_error.value, 'optpos:', c_opt_pos.value
            )

    def test_connection(self) -> None:
        """Tests device connection."""

        status = driver.BL_TestConnection(self._id)

        utils.assert_status_ok(driver=driver, return_code=status)

    def test_communication_speed(
        self, channel: int = 0
        ) -> typing.List[str]:
        """Tests communication speed between computer and instrument.

        Args:
            channel (int, optional): Selected channel.
                Defaults to 0.   

        Returns:
            typing.List[str]: Communication speed between library/device and library/kernel
        """

        c_spd_rcvt = ctypes.c_int32()
        c_spd_kernel = ctypes.c_int32()

        status = driver.BL_TestCommSpeed(
            self._id, channel, ctypes.byref(c_spd_rcvt),
            ctypes.byref(c_spd_kernel)
            )

        utils.assert_status_ok(driver=driver, return_code=status)

        print(
            'communication speed between library and device:',
            c_spd_rcvt.value
            )
        print(
            'communication speed between library and channel:',
            c_spd_kernel.value
            )

        return c_spd_rcvt.value, c_spd_kernel.value

    def disconnect(self) -> None:
        """Disconnects from device."""

        status = driver.BL_Disconnect(self._id)

        utils.assert_status_ok(driver=driver, return_code=status)

        self._id = None
        self._device_info = None

    def load_firmware(
        self,
        channels: list,
        force_reload: bool = False,
        show_gauge: bool = False,
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

        status = driver.BL_LoadFirmware(
            self._id, p_channels, ctypes.byref(c_results),
            len(channels), show_gauge, force_reload,
            ctypes.byref(c_bin_file), ctypes.byref(c_xlx_file)
            )

        utils.assert_status_ok(driver=driver, return_code=status)

        return list(c_results)

    def get_channels_plugged(self, no_channels: int = 1) -> list:
        """Get information about which channels are plugged.

        Returns:
            (list): A boolean list of channels plugged.
        """

        status_ = (ctypes.c_uint8 * no_channels)()
        pstatus = ctypes.cast(status_, ctypes.POINTER(ctypes.c_uint8))

        status = driver.BL_GetChannelsPlugged(
            self._id, pstatus, no_channels
            )

        utils.assert_status_ok(driver=driver, return_code=status)

        return [result == 1 for result in status_]

    def is_channel_plugged(self, channel: int = 0) -> bool:
        """Test if the selected channel is plugged.

        Args:
            channel (int, optional): Selected channel.
                Defaults to 0.
        
        Returns:
            bool: Whether the channel is plugged or not.
        """

        result = driver.BL_IsChannelPlugged(self._id, channel)

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

        driver.BL_GetChannelInfos(
            self._id, channel, ctypes.byref(c_channel_info)
            )

        channel_info = utils.structure_to_dict(
            structure=c_channel_info
            )
        channel_info_parsed = utils.parse_channel_info(
            channel_info=channel_info
            )

        return channel_info_parsed

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

        status = driver.BL_GetMessage(
            self._id, channel, ctypes.byref(message),
            ctypes.byref(size)
            )

        utils.assert_status_ok(driver=driver, return_code=status)

        return message.value.decode()

    def load_technique(
        self,
        technique_path: str,
        c_tecc_params: structures.EccParams,
        first: bool = True,
        last: bool = True,
        channel: int = 0
        ) -> None:
        """Load a technique onto the specified channel.

        Args:
            c_technique_params (structures.TEccParams): Structure of
                parameters of selected technique. Refer to documentation
                and module techniques.py for details.
            technique_filename (str): Technique filename w path,
                e.g. 'C:\\Users\\ocv.ecc'.
            first (bool, optional): Whether this technique is the first
                technique. Defaults to True.
            last (bool, optional): Thether this technique is the last
                technique. Defaults to True.
            channel (int, optional): Selected channel. Defaults to 0.
        """

        status = driver.BL_LoadTechnique(
            self._id,
            channel,
            technique_path.encode(),
            c_tecc_params,
            first,
            last,
            False,
            )

        utils.assert_status_ok(driver=driver, return_code=status)

    def start_channel(self, channel: int = 0) -> None:
        """Starts technique loaded on channel.
        
        Args:
            channel (int, optional): Selected channel.
                    Defaults to 0.
        """

        status = driver.BL_StartChannel(self._id, channel)

        utils.assert_status_ok(driver=driver, return_code=status)

    def stop_channel(self, channel: int = 0) -> None:
        """Stops technique loaded on channel.

        Args:
            channel (int, optional): Selected channel.
                    Defaults to 0.
        """

        status = driver.BL_StopChannel(self._id, channel)

        utils.assert_status_ok(driver=driver, return_code=status)

    def get_current_values(self, channel: int = 0) -> dict:
        """Get the current values for the spcified channel.
        
        Args:
            channel (int, optional): Selected channel.
                    Defaults to 0.
        
        Returns:
            dict: A dict of current values information
        """

        c_current_values = structures.CurrentValues()

        status = driver.BL_GetCurrentValues(
            self._id, channel, ctypes.byref(c_current_values)
            )

        utils.assert_status_ok(driver=driver, return_code=status)

        # Convert the struct to a dict and translate a few values
        current_values = utils.structure_to_dict(c_current_values)
        current_values['State(translated)'] = constants.State(
            current_values['State']
            ).name
        current_values['IRange(translated)'] = constants.CurrentRange(
            current_values['IRange']
            ).name

        print('\n\n\n')
        print(current_values)

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

        status = driver.BL_GetData(
            self._id,
            channel,
            p_data_buffer,
            ctypes.byref(c_data_infos),
            ctypes.byref(c_current_values),
            )

        utils.assert_status_ok(driver=driver, return_code=status)

        # The KBIOData will ask the appropriate techniques for which data
        # fields they return data in
        data = handler.KBIOData(
            c_databuffer, c_data_infos, c_current_values, self
            )

        if data.technique == 'KBIO_TECHID_NONE':
            data = None

        return data


class HCP1005(GeneralPotentiostat):
    """Specific driver for the HCP-1005 potentiostat"""

    def __init__(self):
        """Initialize the HCP-1005 potentiostat driver.
        Refer to superclass initializer for arguments.
        """

        super(HCP1005, self).__init__(type_='KBIO_DEV_HCP1005')


class SP150(GeneralPotentiostat):
    """Specific driver for the SP-150 potentiostat"""

    def __init__(self):
        """Initialize the HCP-1005 potentiostat driver.
        Refer to superclass initializer for arguments.
        """

        super(SP150, self).__init__(type_='KBIO_DEV_SP150')


#--------------------------------------------------------------------------------#
# Driver functions independent of self._id -> keeping detached from main class to reduce coupling.


def convert_numeric_to_single(numeric: int) -> float:
    """Converts a numeric (integer) into a float.

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
        numeric (int): Integer representing a float
    
    Returns:
        float: The float value.
    """

    c_out_float = ctypes.c_float()

    status = driver.BL_ConvertNumericIntoSingle(
        numeric, ctypes.byref(c_out_float)
        )

    utils.assert_status_ok(driver=driver, return_code=status)

    return c_out_float.value
