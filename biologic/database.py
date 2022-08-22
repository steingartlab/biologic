"""Employs the mqtt protocol to relay data stream to database."""

import paho.mqtt.client as mqtt
import json

from biologic import config

class Database:
    """Establishes a one-way connection to Drops to push data through
    the mqtt protocol.

    Attributes:
        self.client: The mqtt-client responsible for starting and
            maintaining the connection.

    Example:
        path = 'test'
        table = 'exp_xx'
        db = database.Database(path=path)
        while *data is being updated*:
            db.write(payload, table)
    """

    def __init__(self, path: str):
        """
        Args:
            path (str): Path in Drops hierarchy w/o leading or
            trailing slashes.
        """

        self.client = mqtt.Client()
        self.client.connect(
            host=config.host,
            port=config.port,
            keepalive=3600
        )
        self.client.loop_start()

        self.url = f'{config.drops_prefix}/{path}/'

    def write(self, payload: dict, table: str = 'table') -> mqtt.MQTTMessageInfo:
        """Writes data out to Drops.
        Args:
            payload (dict): The output data.
            table (str, optional): Table name in database.
                Defaults to 'table'.
        Returns:
            mqtt.MQTTMessageInfo: Contains property *is_published*
                for checking if writeout was successful.
        """

        destination = f'{self.url}{str(table)}'

        return self.client.publish(
            topic=destination,
            payload=json.dumps(payload)
        )
