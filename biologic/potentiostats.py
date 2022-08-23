"""Classes containing methods for using EC-Lab drivers to communicate with BioLogic potentiostat."""

import ctypes
import json
import typing

from biologic import constants, handler, structures, utils

with open('biologic\\config.json', 'r') as f:
    settings = json.load(f)

DRIVERPATH = settings['driverpath']


class InstrumentFinder:
    """Finds BioLogic instruments connected via ethernet.
    
    Attributes:
        self.usb_port (str): Instrument IP-address, e.g. '192.168.0.1'.
        self.instrument_type (str): Instrument type, e.g. 'SP-150'.
    """

    def __init__(self, driver: str = 'blfind64.dll'):
        """
        Args:
            driver (str, optional): Driver filename. For distinguishing
                between 32 and 64-bit systems. Defaults to 'blfind64.dll'.
        """
        self.driver = ctypes.WinDLL(DRIVERPATH + driver)
        self._usb_port: str = None
        self._instrument_type: str = None

    @property
    def usb_port(self) -> str:
        """Returns parsed USB port of connected instrument.

        Returns:
            str: Instrument USB port, e.g. 'USB0'.
        """
        return str(self._usb_port)

    @property
    def instrument_type(self) -> str:
        """Returns parsed type of connected instrument.

        Returns:
            str: Instrument type, e.g. 'SP-150'.
        """
        return str(self._instrument_type)

    def save(self):
        with open('biologic\\config.json', 'r') as f:
            config = json.load(f)

        config['usb_port'] = self.usb_port
        config['instrument_type'] = self.instrument_type

        with open('biologic\\config.json', 'w') as f:
            json.dump(config, f, ensure_ascii=False)

    def find(self, bytes_: int = 255) -> None:
        """Searches for ethernet-connected BioLogic potentiostats.

        Args:
            bytes_ (int, optional): Number of bytes to allocate to buffer.
                Defaults to 255.
        """

        lst_dev = ctypes.create_string_buffer(bytes_)
        size = ctypes.c_uint32(bytes_)
        nbr_dev = ctypes.c_uint32(bytes_)

        status = self.driver.BL_FindEChemUsbDev(
            ctypes.byref(lst_dev),
            ctypes.byref(size),
            ctypes.byref(nbr_dev)
            )

        utils.assert_status_ok(driver=self.driver, return_code=status)
        utils.assert_one_device(c_nbr_dev=nbr_dev)

        self._usb_port, self._instrument_type = utils.parse_potentiostat_search(
            bytes_string=lst_dev
            )

        self.save()


class Potentiostat:
    """BioLogic baseclass. Specific potentiostat types inherit from this class.

    Contains exclusively methods for running experiments (in sequential order),
    as opposed to subclass Config, which contains methods for setting up,
    debugging, and configuring new ones.

    Attributes:
        self.channel (int): The channel on which the potentiostat resides.
        self._type (str): Potentiostat type.
        self._id (ctypes.c_int32): Potentistat id, passed to all functions
            calling instrument.
        self._device_info (structures.DeviceInfo):

    Raises:
        ECLibError: All class class methods use the EC-lib DLL
            communications library to talk with the equipment and they will
            raise this exception if this library reports an error. It will not
            be explicitly mentioned in every single method.
    """

    def __init__(
        self,
        channel: int = 0,
        type_: str = None,
        driver: str = 'EClib64.dll'
        ):
        """Initialize the potentiostat driver.

        Args:
            type_ (str, optional): Device type, e.g. 'KBIO_DEV_HCP1005'.
        
        Raises:
            WindowsError: If driver isn't found.
        """

        self.channel = channel
        self._type = type_

        self._id = None
        self._device_info = None

        self.driver = ctypes.WinDLL(DRIVERPATH + driver)

    def connect(self, usb_port: str, timeout: int = 5) -> None:
        """Connects to instrument and returns device info.
        
        Args:
            usb_port (str): IP-address of device, e.g. from
                InstrumentFinder.find().
            timeout (int, optional): Wait for timeout number of seconds
                before timing out. Defaults to 5.
        
        Raises:
            ECLibCustomException: If class instance doesn't match device type.
        """

        address = ctypes.create_string_buffer(usb_port.encode())
        self._id = ctypes.c_int32()
        self._device_info = structures.DeviceInfos()

        status = self.driver.BL_Connect(
            ctypes.byref(address), ctypes.c_uint8(timeout),
            ctypes.byref(self._id), ctypes.byref(self._device_info)
            )

        utils.assert_status_ok(driver=self.driver, return_code=status)

        utils.assert_device_type_ok(
            device_code=self._device_info.DeviceCode,
            reference_device=self._type
            )

    def load_technique(
        self,
        technique_path: str,
        c_tecc_params: structures.EccParams,
        first: bool = True,
        last: bool = True
        ) -> None:
        """Load a technique onto the specified channel.

        Args:
            c_technique_params (structures.TEccParams): Structure of
                parameters of selected technique. Refer to documentation
                and module techniques.py for details.
            technique_filename (str): Technique filename w relative path,
                e.g. 'drivers\\ocv.ecc'.
            first (bool, optional): Whether this technique is the first
                technique. Defaults to True.
            last (bool, optional): Thether this technique is the last
                technique. Defaults to True.
        """

        status = self.driver.BL_LoadTechnique(
            self._id,
            self.channel,
            technique_path.encode(),
            c_tecc_params,
            first,
            last,
            False,
            )

        utils.assert_status_ok(driver=self.driver, return_code=status)

    def start_channel(self) -> None:
        """Starts technique loaded on channel."""

        status = self.driver.BL_StartChannel(self._id, self.channel)

        utils.assert_status_ok(driver=self.driver, return_code=status)

    def get_current_values(self) -> dict:
        """Get the current values for the spcified channel.
        
        Returns:
            dict: A dict of current values information
        """

        c_current_values = structures.CurrentValues()

        status = self.driver.BL_GetCurrentValues(
            self._id, self.channel, ctypes.byref(c_current_values)
            )

        utils.assert_status_ok(driver=self.driver, return_code=status)

        # Convert the struct to a dict and translate a few values
        current_values = utils.structure_to_dict(c_current_values)

        return current_values

    def get_data(self) -> handler.KBIOData:
        """Get data for the specified channel.
        
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
            self.channel,
            p_data_buffer,
            ctypes.byref(c_data_infos),
            ctypes.byref(c_current_values),
            )

        utils.assert_status_ok(driver=self.driver, return_code=status)

        # The KBIOData will ask the appropriate techniques for which data
        # fields they return data in
        data = handler.KBIOData(
            c_databuffer, c_data_infos, c_current_values, self
            )

        if data.technique == 'KBIO_TECHID_NONE':
            data = None

        return data

    def stop_channel(self) -> None:
        """Stops technique loaded on channel."""

        status = self.driver.BL_StopChannel(self._id, self.channel)

        utils.assert_status_ok(driver=self.driver, return_code=status)

    def disconnect(self) -> None:
        """Disconnects from device."""

        status = self.driver.BL_Disconnect(self._id)

        utils.assert_status_ok(driver=self.driver, return_code=status)

        self._id = None
        self._device_info = None


class HCP1005(Potentiostat):
    """Specific driver for the HCP-1005 potentiostat"""

    def __init__(self):
        """Initialize the HCP-1005 potentiostat driver.
        Refer to superclass initializer for arguments.
        """

        super(HCP1005, self).__init__(type_='KBIO_DEV_HCP1005')


class SP150(Potentiostat):
    """Specific driver for the SP-150 potentiostat"""

    def __init__(self):
        """Initialize the HCP-1005 potentiostat driver.
        Refer to superclass initializer for arguments.
        """

        super(SP150, self).__init__(type_='KBIO_DEV_SP150')


class Config(Potentiostat):
    """This subclass of Potentiostat is for setting up,
    debugging, and configuring potentiostats.

    It does not explicitly contain any of the methods
    for running experiments but calling Potentiostat.connect()
    is necessary to run the config.
    """

    def __init__(self, type):
        super(Config, self).__init__(type_=type)

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

    def get_channel_info(self) -> dict:
        """Get information about the specified channel.

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
            self._id, self.channel, ctypes.byref(c_channel_info)
            )

        channel_info = utils.structure_to_dict(
            structure=c_channel_info
            )
        channel_info_parsed = utils.parse_channel_info(
            channel_info=channel_info
            )

        return channel_info_parsed

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

        utils.assert_status_ok(driver=self.driver, return_code=status)

        return [result == 1 for result in status_]

    def get_error_status(self):
        """Retrive current error status from potentiostat."""

        c_opt_error = ctypes.c_int32()
        c_opt_pos = ctypes.c_int32()

        status = self.driver.BL_GetOptErr(
            self._id, self.channel, ctypes.byref(c_opt_error),
            ctypes.byref(c_opt_pos)
            )

        utils.assert_status_ok(driver=self.driver, return_code=status)

    def is_channel_plugged(self) -> bool:
        """Test if the selected channel is plugged.

        Args:
            channel (int, optional): Selected channel.
                Defaults to 0.
        
        Returns:
            bool: Whether the channel is plugged or not.
        """

        result = self.driver.BL_IsChannelPlugged(
            self._id, self.channel
            )

        return bool(result)

    def get_message(self) -> str:
        """Return a message from the firmware of a channel.
        
        Returns:
            str: Board description.
        """

        size = ctypes.c_uint32(255)
        message = ctypes.create_string_buffer(255)

        status = self.driver.BL_GetMessage(
            self._id, self.channel, ctypes.byref(message),
            ctypes.byref(size)
            )

        utils.assert_status_ok(driver=self.driver, return_code=status)

        return message.value.decode()

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

        bin_file: str = DRIVERPATH + kernel
        c_bin_file = ctypes.create_string_buffer(bin_file.encode())

        xlx_file: str = DRIVERPATH + xlx
        c_xlx_file = ctypes.create_string_buffer(xlx_file.encode())

        status = self.driver.BL_LoadFirmware(
            self._id, p_channels, ctypes.byref(c_results),
            len(channels), show_gauge, force_reload,
            ctypes.byref(c_bin_file), ctypes.byref(c_xlx_file)
            )

        utils.assert_status_ok(driver=self.driver, return_code=status)

        return list(c_results)

    def test_connection(self) -> None:
        """Tests device connection."""

        status = self.driver.BL_TestConnection(self._id)

        utils.assert_status_ok(driver=self.driver, return_code=status)

    def test_communication_speed(self) -> typing.List[str]:
        """Tests communication speed between computer and instrument.

        Returns:
            typing.List[str]: Communication speed between library/device and library/kernel
        """

        c_spd_rcvt = ctypes.c_int32()
        c_spd_kernel = ctypes.c_int32()

        status = self.driver.BL_TestCommSpeed(
            self._id, self.channel, ctypes.byref(c_spd_rcvt),
            ctypes.byref(c_spd_kernel)
            )

        utils.assert_status_ok(driver=self.driver, return_code=status)

        # print(
        #     'communication speed between library and device:',
        #     c_spd_rcvt.value
        #     )
        # print(
        #     'communication speed between library and channel:',
        #     c_spd_kernel.value
        #     )

        return c_spd_rcvt.value, c_spd_kernel.value