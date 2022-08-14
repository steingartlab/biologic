from enum import Enum, auto


class AutoEnum(Enum):
    """Zero-based auto enum because I do be specific like that."""

    def _generate_next_value_(name, start, count, last_values):
        if len(last_values) > 0:
            return last_values[-1] + 1
        return 0


class Device(AutoEnum):
    KBIO_DEV_VMP = auto()
    KBIO_DEV_VMP2 = auto()
    KBIO_DEV_MPG = auto()
    KBIO_DEV_BISTA = auto()
    KBIO_DEV_MCS200 = auto()
    KBIO_DEV_VMP3 = auto()
    KBIO_DEV_VSP = auto()
    KBIO_DEV_HCP803 = auto()
    KBIO_DEV_EPP400 = auto()
    KBIO_DEV_EPP4000 = auto()
    KBIO_DEV_BISTAT2 = auto()
    KBIO_DEV_FCT150S = auto()
    KBIO_DEV_VMP300 = auto()
    KBIO_DEV_SP50 = auto()
    KBIO_DEV_SP150 = auto()
    KBIO_DEV_FCT50S = auto()
    KBIO_DEV_SP300 = auto()
    KBIO_DEV_CLB500 = auto()
    KBIO_DEV_HCP1005 = auto()
    KBIO_DEV_CLB2000 = auto()
    KBIO_DEV_VSP300 = auto()
    KBIO_DEV_SP200 = auto()
    KBIO_DEV_MPG2 = auto()
    KBIO_DEV_SP100 = auto()
    KBIO_DEV_MOSLED = auto()
    KBIO_DEV_SP240 = auto()
    KBIO_DEV_UNKNOW = auto()


class Firmware(AutoEnum):
    KBIO_FIRM_NONE = auto()
    KBIO_FIRM_INTERPR = auto()
    KBIO_FIRM_UNKNOWN = auto()
    KBIO_FIRM_KERNEL = auto()
    KBIO_FIRM_INVALID = auto()
    KBIO_FIRM_ECAL = auto()


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
    KBIO_STATE_STOP = auto()
    KBIO_STATE_RUN = auto()
    KBIO_STATE_PAUSE = auto()


class Technique(Enum):
    KBIO_TECHID_NONE = 0
    KBIO_TECHID_OCV = 100
    KBIO_TECHID_CA = auto()
    KBIO_TECHID_CP = auto()
    KBIO_TECHID_CV = auto()
    KBIO_TECHID_PEIS = auto()
    KBIO_TECHID_POTPULSE = auto()
    KBIO_TECHID_GALPULSE = auto()
    KBIO_TECHID_GEIS = auto()
    KBIO_TECHID_STACKPEIS_SLAVE = auto()
    KBIO_TECHID_STACKPEIS = auto()
    KBIO_TECHID_CPOWER = auto()
    KBIO_TECHID_CLOAD = auto()
    KBIO_TECHID_FCT = auto()
    KBIO_TECHID_SPEIS = auto()
    KBIO_TECHID_SGEIS = auto()
    KBIO_TECHID_STACKPDYN = auto()
    KBIO_TECHID_STACKPDYN_SLAVE = auto()
    KBIO_TECHID_STACKGDYN = auto()
    KBIO_TECHID_STACKGEIS_SLAVE = auto()
    KBIO_TECHID_STACKGEIS = auto()
    KBIO_TECHID_STACKGDYN_SLAVE = auto()
    KBIO_TECHID_CPO = auto()
    KBIO_TECHID_CGA = auto()
    KBIO_TECHID_COKINE = auto()
    KBIO_TECHID_PDYN = auto()
    KBIO_TECHID_GDYN = auto()
    KBIO_TECHID_CVA = auto()
    KBIO_TECHID_DPV = auto()
    KBIO_TECHID_SWV = auto()
    KBIO_TECHID_NPV = auto()
    KBIO_TECHID_RNPV = auto()
    KBIO_TECHID_DNPV = auto()
    KBIO_TECHID_DPA = auto()
    KBIO_TECHID_EVT = auto()
    KBIO_TECHID_LP = auto()
    KBIO_TECHID_GC = auto()
    KBIO_TECHID_CPP = auto()
    KBIO_TECHID_PDP = auto()
    KBIO_TECHID_PSP = auto()
    KBIO_TECHID_ZRA = auto()
    KBIO_TECHID_MIR = auto()
    KBIO_TECHID_PZIR = auto()
    KBIO_TECHID_GZIR = auto()
    KBIO_TECHID_LOOP = 150
    KBIO_TECHID_TO = auto()
    KBIO_TECHID_TI = auto()
    KBIO_TECHID_TOS = auto()
    KBIO_TECHID_CPLIMIT = 155
    KBIO_TECHID_GDYNLIMIT = auto()
    KBIO_TECHID_CALIMIT = auto()
    KBIO_TECHID_PDYNLIMIT = auto()
    KBIO_TECHID_LASV = auto()
    KBIO_TECHID_MP = 167
    KBIO_TECHID_CASG = 169
    KBIO_TECHID_CASP = auto()
