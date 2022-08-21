import json
import logging
import os
import threading
from time import sleep

from biologic import constants, database, potentiostats, techniques, utils

log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(filename=log_filename,
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

with open('biologic\\config.json') as f:
    settings = json.load(f)

ip_address = settings['ip_address']


class Experiment:

    def __init__(self):
        self._status = 'running'

    @property
    def status(self):
        return self._status

    def check_status(self, state: int) -> None:
        self._status = constants.State(state).name


def run(
    potentiostat: potentiostats.Potentiostat, raw_params: dict,
    pill: threading.Event
    ):
    """Wrapper for running experiments.


    Args:
        potentiostat (potentiostats.Potentiostat): Instance of (a subclass of)
            a potentiostat.
        raw_params (dict): 
        pill (threading.Event): Emergency safety button if an experiment must be
            externally terminated.
    
    """

    potentiostat.connect(ip_address=ip_address)

    parsed_params, tecc_ecc_path, path = utils.parse_raw_params(
        raw_params=raw_params
        )

    db = database.Database(path=path)

    c_tecc_params = techniques.set_technique_params(parsed_params)

    potentiostat.load_technique(
        technique_path=tecc_ecc_path, c_tecc_params=c_tecc_params
        )
    potentiostat.start_channel()

    experiment = Experiment()

    try:
        while experiment.status == 'running' and not pill.wait(1):
            current_values = potentiostat.get_current_values()
            payload = utils.parse_payload(raw_data=current_values)
            # This writes to Drops, but I might have also to send data directly to
            # brix if brix cannot retrieve data fast enough. I'll cross that bridge when I get there
            # Also have to write some sort of asyncio mechanism for brix.
            db.write(payload=payload, table='biologic')
            experiment.check_status(state=current_values['State'])
            print(experiment.status)
    except Exception as e:
        pill.set()
        logging.error(e)