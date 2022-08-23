"""Flask app connecting pithy container to biologic container"""

import flask
import logging
import os
from threading import Event, Thread
import werkzeug

from biologic import experiment, potentiostats

log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(filename=log_filename,
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

PORT = '5002'

app = flask.Flask(__name__)


def configure_routes(app):

    @app.route('/')
    def hello_world():
        """Establish initial connection.
        
        Returns:
            str: Status message
        """

        return "Flask BioLogic server running"

    # Runs resonance
    @app.route('/run', methods=['POST'])
    def run():
        """This is where the magic happens.
        """

        if 'experiment_' not in globals():
            global experiment_
            experiment_ = experiment.Experiment()

        if experiment_.status == 'running':
            return "Aborted: Experiment already running"

        global pill, potentiostat

        pill = Event()  # kills thread when called
        potentiostat = potentiostats.HCP1005()

        params = flask.request.json

        global thread
        thread = Thread(target=experiment.run,
               args=(potentiostat, params, pill, experiment_))

        thread.start()

        return 'Technique started'

    @app.route('/check_status')
    def check_status():
        if 'experiment_' not in globals():
            return 'No experiment instance in scope'

        return experiment_.status

    @app.route('/stop')
    def stop():
        """A big, fat, virtual emergency stop button.
        
        Does two things:
            (1) Stops the running technique.
            (2) Stops data logging.
        """

        potentiostat.stop_channel()
        pill.set()

        return "Technique stopped"


    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return '', 404

    @app.route('/block')
    def block():
        """Only for testing purposes."""
        if 'thread' not in globals():
            return "Thread nonexistent"
        
        thread.join()

        return "Thread joined"



configure_routes(app)

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", debug=True)
