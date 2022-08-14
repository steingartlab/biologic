"""Wrapper."""

import time
from biologic.potentiostats import HCP1005
import biologic.techniques


def run_ocv():
    """Test the OCV technique"""
    ip_address = '192.168.0.257'  # REPLACE THIS WITH A VALID IP
    # Instantiate the instrument and connect to it
    sp150 = HCP1005(ip_address)
    sp150.connect()

    # Instantiate the technique. Make sure to give values for all the
    # arguments where the default values does not fit your purpose. The
    # default values can be viewed in the API documentation for the
    # technique.
    ocv = biologic.techniques.OCV(
        rest_time_T=0.2, record_every_dE=10.0, record_every_dT=0.01
        )

    # Load the technique onto channel 0 of the potentiostat and start it
    sp150.load_technique(0, ocv)
    sp150.start_channel(0)

    time.sleep(0.1)
    while True:
        # Get the currently available data on channel 0 (only what has
        # been gathered since last get_data)
        data_out = sp150.get_data(0)

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

    sp150.stop_channel(0)
    sp150.disconnect()


if __name__ == '__main__':
    run_ocv()