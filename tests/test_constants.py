from biologic import constants

def test_zero_based_auto_enum():
    current_range = constants.State['paused'].value

    assert current_range == 2