"""Wrapper."""

import time

from biologic import potentiostats, techniques


def find():
    finder = potentiostats.InstrumentFinder()

    return finder.find()


def run_ocv(ip_address: str):
    """Test the OCV technique"""
    # Instantiate the instrument and connect to it
    potentiostat = potentiostats.HCP1005(ip_address)
    potentiostat.connect()

    channels = None
    potentiostat.is_channel_plugged(channel=channel)
    potentiostat.load_firmware(channels=channels, force_reload=True)
    # Instantiate the technique. Make sure to give values for all the
    # arguments where the default values does not fit your purpose. The
    # default values can be viewed in the API documentation for the
    # technique.
    ocv = techniques.OCV(
        rest_time_T=0.2, record_every_dE=10.0, record_every_dT=0.01
        )

    # Load the technique onto channel 0 of the potentiostat and start it
    potentiostat.load_technique(0, ocv)
    potentiostat.start_channel(0)

    time.sleep(0.1)
    while True:
        # Get the currently available data on channel 0 (only what has
        # been gathered since last get_data)
        data_out = potentiostat.get_data(0)

        # If there is none, assume the technique has finished
        if data_out is None:
            break

        # The data is available in lists as attributes on the data
        # object. The available data fields are listed in the API
        # documentation for the technique.
        print("Time:", data_out.time)
        print("Ewe:", data_out.Ewe)

        # If numpy is installed, the data can also be retrieved as
        # numpy arrays
        #print('Time:', data_out.time_numpy)
        #print('Ewe:', data_out.Ewe_numpy)
        time.sleep(0.1)

    potentiostat.stop_channel(0)
    potentiostat.disconnect()


if __name__ == '__main__':
    ip_address = find()
    print(ip_address)
    run_ocv(ip_address=ip_address)