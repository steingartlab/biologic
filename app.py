"""Flask app connecting pithy container to biologic container"""

import flask
import json
import logging
import os
import werkzeug

log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(filename=log_filename,
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

PORT = '5002'

app = flask.Flask(__name__)


def configure_routes(app):
    from biologic import potentiostat, technique

    @app.route('/')
    def hello_world():
        """
        Returns:
            Str: Status message
        """
        return "Flask BioLogic server running"

    # Runs resonance
    @app.route('/cycle', methods=['POST'])
    def get_resonance():
        """This is where the magic happens.
        Receives params from pithy, passes them onto the potentiostat,
        receives data from the potentiostat, and finally returns the data
        Returns:
            dict: waveform data
        """

        data = ''


        return json.dumps(data)


    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return '', 404


configure_routes(app)

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", debug=True)
