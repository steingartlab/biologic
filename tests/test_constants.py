from biologic import constants

def test_zero_based_auto_enum():
    device_code = constants.Device['KBIO_DEV_VMP'].value
    
    assert device_code == 0