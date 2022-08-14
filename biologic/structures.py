import ctypes


class ChannelInfos(ctypes.Structure):
    """Channel information structure"""
    _fields_ = [
        ('Channel', ctypes.c_int32),
        ('BoardVersion', ctypes.c_int32),
        ('BoardSerialNumber', ctypes.c_int32),
        # Translated to string with FIRMWARE_CODES
        ('FirmwareCode', ctypes.c_int32),
        ('FirmwareVersion', ctypes.c_int32),
        ('XilinxVersion', ctypes.c_int32),
        # Translated to string with AMP_CODES
        ('AmpCode', ctypes.c_int32),
        # NbAmp is not mentioned in the documentation, but is in
        # in the examples and the info does not make sense
        # without it
        ('NbAmp', ctypes.c_int32),
        ('LCboard', ctypes.c_int32),
        ('Zboard', ctypes.c_int32),
        ('MUXboard', ctypes.c_int32),
        ('GPRAboard', ctypes.c_int32),
        ('MemSize', ctypes.c_int32),
        ('MemFilled', ctypes.c_int32),
        # Translated to string with STATES
        ('State', ctypes.c_int32),
        # Translated to string with MAX_I_RANGES
        ('MaxIRange', ctypes.c_int32),
        # Translated to string with MIN_I_RANGES
        ('MinIRange', ctypes.c_int32),
        # Translated to string with MAX_BANDWIDTHS
        ('MaxBandwidth', ctypes.c_int32),
        ('NbOfTechniques', ctypes.c_int32),
        ]


class CurrentValues(ctypes.Structure):
    """Current values structure"""
    _fields_ = [
        # Translate to string with STATES
        ('State', ctypes.c_int32),  # Channel state
        ('MemFilled', ctypes.c_int32),  # Memory filled (in Bytes)
        ('TimeBase', ctypes.c_float),  # Time base (s)
        ('Ewe', ctypes.c_float),  # Working electrode potential (V)
        ('EweRangeMin', ctypes.c_float),  # Ewe min range (V)
        ('EweRangeMax', ctypes.c_float),  # Ewe max range (V)
        ('Ece', ctypes.c_float),  # Counter electrode potential (V)
        ('EceRangeMin', ctypes.c_float),  # Ece min range (V)
        ('EceRangeMax', ctypes.c_float),  # Ece max range (V)
        ('Eoverflow', ctypes.c_int32),  # Potential overflow
        ('I', ctypes.c_float),  # Current value (A)
        # Translate to string with IRANGE
        ('IRange', ctypes.c_int32),  # Current range
        ('Ioverflow', ctypes.c_int32),  # Current overflow
        ('ElapsedTime', ctypes.c_float),  # Elapsed time
        ('Freq', ctypes.c_float),  # Frequency (Hz)
        ('Rcomp', ctypes.c_float),  # R-compenzation (Ohm)
        ('Saturation', ctypes.c_int32),  # E or/and I saturation
        ]
    # Hack to include the fields names in doc string (and Sphinx documentation)
    __doc__ += '\n\n    Fields:\n\n' + '\n'.join(
        ['    * {} {}'.format(*field) for field in _fields_]
        )


class DataInfos(ctypes.Structure):
    """DataInfos structure"""
    _fields_ = [
        ('IRQskipped', ctypes.c_int32),  # Number of IRQ skipped
        ('NbRaws',
         ctypes.c_int32),  # Number of raws into the data buffer,
        # i.e. number of points saced in the
        # data buffer
        ('NbCols', ctypes.c_int32),  # Number of columns into the data
        # buffer, i.e. number of variables
        # defining a point in the data buffer
        ('TechniqueIndex', ctypes.c_int32),  # Index (0-based) of the
        # technique that has generated
        # the data
        ('TechniqueID', ctypes.c_int32
        ),  # Identifier of the technique that
        # has generated the data
        ('ProcessIndex', ctypes.c_int32
        ),  # Index (0-based) of the process
        # of the technique that ahs
        # generated the data
        ('loop', ctypes.c_int32),  # Loop number
        ('StartTime', ctypes.c_double),  # Start time (s)
        ]
    # Hack to include the fields names in doc string (and Sphinx documentation)
    __doc__ += '\n\n    Fields:\n\n' + '\n'.join(
        ['    * {} {}'.format(*field) for field in _fields_]
        )


class DeviceInfos(ctypes.Structure):
    """Device information struct"""
    _fields_ = [  # Translated to string with DEVICE_CODES
        ('DeviceCode', ctypes.c_int32),
        ('RAMsize', ctypes.c_int32),
        ('CPU', ctypes.c_int32),
        ('NumberOfChannels', ctypes.c_int32),
        ('NumberOfSlots', ctypes.c_int32),
        ('FirmwareVersion', ctypes.c_int32),
        ('FirmwareDate_yyyy', ctypes.c_int32),
        ('FirmwareDate_mm', ctypes.c_int32),
        ('FirmwareDate_dd', ctypes.c_int32),
        ('HTdisplayOn', ctypes.c_int32),
        ('NbOfConnectedPC', ctypes.c_int32)
    ]


class TECCParam(ctypes.Structure):
    """Technique parameter"""
    _fields_ = [
        ('ParamStr', ctypes.c_char * 64),
        ('ParamType', ctypes.c_int32),
        ('ParamVal', ctypes.c_int32),
        ('ParamIndex', ctypes.c_int32),
        ]
    # Hack to include the fields names in doc string (and Sphinx documentation)
    __doc__ += '\n\n    Fields:\n\n' + '\n'.join(
        ['    * {} {}'.format(*field) for field in _fields_]
        )


class TECCParams(ctypes.Structure):
    """Technique parameters"""
    _fields_ = [
        ('len', ctypes.c_int32),
        ('pParams', ctypes.POINTER(TECCParam)),
        ]
    # Hack to include the fields names in doc string (and Sphinx documentation)
    __doc__ += '\n\n    Fields:\n\n' + '\n'.join(
        ['    * {} {}'.format(*field) for field in _fields_]
        )
