import json
import logging
import os
from threading import Event

from biologic.config import slack_user_id, slack_channel_url
from biologic.constants import State
from biologic.database import Database
from biologic.potentiostats import Potentiostat
from biologic import slackbot
from biologic.techniques import set_technique_params
from biologic.utils import parse_raw_params, parse_payload


log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(filename=log_filename,
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

with open('biologic\\config.json') as f:
    settings = json.load(f)

usb_port = settings['usb_port']


class Experiment:

    def __init__(self):
        self._status = 'stopped'

    @property
    def status(self):
        return self._status

    def set_status(self, status: str):
        self._status = status

    def check_status(self, state: int) -> None:
        self._status = State(state).name


def run(potentiostat: Potentiostat, raw_params: dict, pill: Event, experiment_: Experiment):
    """Wrapper for running experiments.

    Args:
        potentiostat (potentiostats.Potentiostat): Instance of (a subclass of)
            a potentiostat.
        raw_params (dict): 
        pill (threading.Event): Emergency stop button if an experiment must be
            externally terminated.
    """

    parsed_params, technique_paths, db_path = parse_raw_params(
        raw_params=raw_params
        )
    db = Database(path=db_path)
    c_tecc_params = set_technique_params(parsed_params)
    potentiostat.connect(usb_port=usb_port)
    potentiostat.load_technique(
        technique_paths=technique_paths, c_tecc_params=c_tecc_params
        )
    potentiostat.start_channel()

    experiment_.set_status('running')

    try:
        while experiment_.status == 'running' and not pill.wait(1):
            data_infos, current_values = potentiostat.get_data()
            payload = parse_payload(raw_data=current_values, raw_metadata=data_infos)
            db.write(payload=payload, table='biologic')
            experiment_.check_status(state=current_values['State'])

    except Exception as e:
        pill.set()
        logging.error(e)

    finally:
        message = f'experiment {raw_params["exp_id"]} finished'
        slackbot.post(
            message=message,
            user_id=slack_user_id,
            url=slack_channel_url
            )
