"""Contains subclasses of ctypes.Structure for necessary type conversions between
the python interface and the lower-level drivers.
"""

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


class POD(ctypes.Structure):
    """ctypes Structure with helper methods."""

    @property
    def keys(self):
        """Reproduce a dict behaviour."""
        
        keys = (t[0] for t in self._fields_)

        return keys

    def __repr__(self):
        """Return class name and fields one at a line."""

        entries = str(self).split(', ')
        cls = type(self).__name__
        en_clair = f"{cls} :\n  " + '\n  '.join(entries)

        return en_clair

    def __str__(self):
        """Return key-value pairs separated by commas."""
        
        entries = list()
        
        for name in self.keys:
            entries.append(f"{name}={getattr(self,name)}")
        
        en_clair = ', '.join(entries)
        
        return en_clair

    def __getattr__(self, name):
        """Access Structure fields with nested attributes."""
        i = name.rfind('.')
        
        if i == -1:
            # Structure should already have provided the first level attribute.
            raise AttributeError(
                f"{type(self)} has no '{name}' attribute"
                )
        
        o = getattr(self, name[:i])
        v = getattr(o, name[i + 1:])

        return v

    def subset(self, *fields):
        """Create a dict from a selection of Structure fields."""
        
        subset = dict()
        
        if len(fields) == 0:
            # no field means all fields
            fields = self.keys
        
        for name in fields:
            value = getattr(self, name)
            subset += {name: value}
        return subset


class EccParam(POD):
    _fields_ = [
        ("ParamStr", 64 * ctypes.c_byte),
        ("ParamType", ctypes.c_int32),
        ("ParamVal", ctypes.c_uint32),
        ("ParamIndex", ctypes.c_int32),
        ]

ECC_PARM = ctypes.POINTER(EccParam)

class EccParams(POD):
    _pack_ = 4
    _fields_ = [
        ("len", ctypes.c_int32),
        ("pParams", ECC_PARM),
        ]