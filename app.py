"""Flask app connecting pithy container to biologic container"""

import flask
import logging
import os
import threading
import werkzeug

from biologic import experiment, potentiostats

log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(filename=log_filename,
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

PORT = '5002'

app = flask.Flask(__name__)

pill = threading.Event()  # kills thread when called
potentiostat = potentiostats.HCP1005()


def configure_routes(app):

    @app.route('/')
    def hello_world():
        """
        Returns:
            Str: Status message
        """
        return "Flask BioLogic server running"

    # Runs resonance
    @app.route('/run', methods=['POST'])
    def get_resonance():
        """This is where the magic happens.
        Receives params from pithy, passes them onto the potentiostat,
        receives data from the potentiostat, and finally returns the data
        Returns:
            dict: waveform data
        """

        if experiment.status == 'running':
            return "Aborted: Experiment already running"

        params = flask.request.values.to_dict()
        
        experiment.run(
            potentiostat=potentiostat,
            raw_params=params,
            pill=pill
        )

        return "Technique started"

    @app.route('/stop')
    def stop():
        pill.set()
        potentiostat.stop_channel()
        potentiostat.disconnect()

        return "Technique stoppped"


    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return '', 404


configure_routes(app)

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", debug=True)
