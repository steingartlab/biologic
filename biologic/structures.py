"""Contains subclasses of Structure for necessary type conversions between
the python interface and the lower-level drivers.
"""

from ctypes import Structure, c_int32, c_float, c_double, POINTER, c_uint32, c_byte


class ChannelInfos(Structure):
    """Channel information structure"""
    _fields_ = [
        ('Channel', c_int32),
        ('BoardVersion', c_int32),
        ('BoardSerialNumber', c_int32),
        # Translated to string with FIRMWARE_CODES
        ('FirmwareCode', c_int32),
        ('FirmwareVersion', c_int32),
        ('XilinxVersion', c_int32),
        # Translated to string with AMP_CODES
        ('AmpCode', c_int32),
        # NbAmp is not mentioned in the documentation, but is in
        # in the examples and the info does not make sense
        # without it
        ('NbAmp', c_int32),
        ('LCboard', c_int32),
        ('Zboard', c_int32),
        ('MUXboard', c_int32),
        ('GPRAboard', c_int32),
        ('MemSize', c_int32),
        ('MemFilled', c_int32),
        # Translated to string with STATES
        ('State', c_int32),
        # Translated to string with MAX_I_RANGES
        ('MaxIRange', c_int32),
        # Translated to string with MIN_I_RANGES
        ('MinIRange', c_int32),
        # Translated to string with MAX_BANDWIDTHS
        ('MaxBandwidth', c_int32),
        ('NbOfTechniques', c_int32),
        ]


class CurrentValues(Structure):
    """Current values structure"""
    _fields_ = [
        # Translate to string with STATES
        ('State', c_int32),  # Channel state
        ('MemFilled', c_int32),  # Memory filled (in Bytes)
        ('TimeBase', c_float),  # Time base (s)
        ('Ewe', c_float),  # Working electrode potential (V)
        ('EweRangeMin', c_float),  # Ewe min range (V)
        ('EweRangeMax', c_float),  # Ewe max range (V)
        ('Ece', c_float),  # Counter electrode potential (V)
        ('EceRangeMin', c_float),  # Ece min range (V)
        ('EceRangeMax', c_float),  # Ece max range (V)
        ('Eoverflow', c_int32),  # Potential overflow
        ('I', c_float),  # Current value (A)
        # Translate to string with IRANGE
        ('IRange', c_int32),  # Current range
        ('Ioverflow', c_int32),  # Current overflow
        ('ElapsedTime', c_float),  # Elapsed time
        ('Freq', c_float),  # Frequency (Hz)
        ('Rcomp', c_float),  # R-compenzation (Ohm)
        ('Saturation', c_int32),  # E or/and I saturation
        ]


class DataInfos(Structure):
    """DataInfos structure"""
    _fields_ = [
        ('IRQskipped', c_int32),  # Number of IRQ skipped
        ('NbRaws',
         c_int32),  # Number of raws into the data buffer,
        # i.e. number of points saved in the
        # data buffer
        ('NbCols', c_int32),  # Number of columns into the data
        # buffer, i.e. number of variables
        # defining a point in the data buffer
        ('TechniqueIndex', c_int32),  # Index (0-based) of the
        # technique that has generated
        # the data
        ('TechniqueID', c_int32
        ),  # Identifier of the technique that
        # has generated the data
        ('ProcessIndex', c_int32
        ),  # Index (0-based) of the process
        # of the technique that ahs
        # generated the data
        ('loop', c_int32),  # Loop number
        ('StartTime', c_double),  # Start time (s)
        ]


class DeviceInfos(Structure):
    """Device information struct"""
    _fields_ = [  # Translated to string with DEVICE_CODES
        ('DeviceCode', c_int32),
        ('RAMsize', c_int32),
        ('CPU', c_int32),
        ('NumberOfChannels', c_int32),
        ('NumberOfSlots', c_int32),
        ('FirmwareVersion', c_int32),
        ('FirmwareDate_yyyy', c_int32),
        ('FirmwareDate_mm', c_int32),
        ('FirmwareDate_dd', c_int32),
        ('HTdisplayOn', c_int32),
        ('NbOfConnectedPC', c_int32)
    ]


class POD(Structure):
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
        ("ParamStr", 64 * c_byte),
        ("ParamType", c_int32),
        ("ParamVal", c_uint32),
        ("ParamIndex", c_int32),
        ]

ECC_PARM = POINTER(EccParam)

class EccParams(POD):
    _pack_ = 4
    _fields_ = [
        ("len", c_int32),
        ("pParams", ECC_PARM),
        ]