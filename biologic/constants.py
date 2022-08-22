"""Constants to aid readability, esp for debugging."""

from dataclasses import dataclass
from enum import Enum, auto
import enum


class AutoEnum(Enum):
    """Zero-based auto enum because I do be specific like that."""

    def _generate_next_value_(name, start, count, last_values):
        if len(last_values) > 0:
            return last_values[-1] + 1
        return 0

@dataclass
class ECC_param:
    """ECC param template"""
    label: str
    type_: type


class Device(Enum):
    """Only including implemented devices."""
    KBIO_DEV_SP150 = 14
    KBIO_DEV_HCP1005 = 18


class Firmware(Enum):
    KBIO_FIRM_NONE = 0
    KBIO_FIRM_INTERPR = 1
    KBIO_FIRM_UNKNOWN = 4
    KBIO_FIRM_KERNEL = 5
    KBIO_FIRM_INVALID = 8
    KBIO_FIRM_ECAL = 10


class Amplifier(AutoEnum):
    KBIO_AMPL_NONE = auto()
    KBIO_AMPL_2A = auto()
    KBIO_AMPL_1A = auto()
    KBIO_AMPL_5A = auto()
    KBIO_AMPL_10A = auto()
    KBIO_AMPL_20A = auto()
    KBIO_AMPL_HEUS = auto()
    KBIO_AMPL_LC = auto()
    KBIO_AMPL_80A = auto()
    KBIO_AMPL_4AI = auto()
    KBIO_AMPL_PAC = auto()
    KBIO_AMPL_4AI_VSP = auto()
    KBIO_AMPL_LC_VSP = auto()
    KBIO_AMPL_UNDEF = auto()
    KBIO_AMPL_MUIC = auto()
    KBIO_AMPL_NONE_GIL = auto()
    KBIO_AMPL_8AI = auto()
    KBIO_AMPL_LB500 = auto()
    KBIO_AMPL_100A5V = auto()
    KBIO_AMPL_LB2000 = auto()
    KBIO_AMPL_1A48V = auto()
    KBIO_AMPL_4A10V = auto()


class CurrentRange(AutoEnum):
    KBIO_IRANGE_100pA = auto()
    KBIO_IRANGE_1nA = auto()
    KBIO_IRANGE_10nA = auto()
    KBIO_IRANGE_100nA = auto()
    KBIO_IRANGE_1uA = auto()
    KBIO_IRANGE_10uA = auto()
    KBIO_IRANGE_100uA = auto()
    KBIO_IRANGE_1mA = auto()
    KBIO_IRANGE_10mA = auto()
    KBIO_IRANGE_100mA = auto()
    KBIO_IRANGE_1A = auto()
    KBIO_IRANGE_BOOSTER = auto()
    KBIO_IRANGE_AUTO = auto()
    KBIO_IRANGE_10pA = auto()  # IRANGE_100pA + Igain x10
    KBIO_IRANGE_1pA = auto()  # IRANGE_100pA + Igain x100


class Bandwidth(Enum):
    KBIO_BW_1 = auto()
    KBIO_BW_2 = auto()
    KBIO_BW_3 = auto()
    KBIO_BW_4 = auto()
    KBIO_BW_5 = auto()
    KBIO_BW_6 = auto()
    KBIO_BW_7 = auto()
    KBIO_BW_8 = auto()
    KBIO_BW_9 = auto()


class VoltageRange(AutoEnum):
    KBIO_ERANGE_2_5 = auto()
    KBIO_ERANGE_5 = auto()
    KBIO_ERANGE_10 = auto()
    KBIO_ERANGE_AUTO = auto()


class State(AutoEnum):
    stopped = auto()
    running = auto()
    paused = auto()


class Technique(Enum):
    """Only including implemented techniques."""
    KBIO_TECHID_NONE = 0
    KBIO_TECHID_OCV = 100
    KBIO_TECHID_CA = 101
    KBIO_TECHID_CP = 102
    KBIO_TECHID_CV = 103
