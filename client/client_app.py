import json
import sys

from PodSixNet.Connection import ConnectionListener, connection

from logger import Logger
from overlay import Overlay

"""All methods starting with capital letter are network related"""

class Client(ConnectionListener):
    def __init__(self):
        # Create logger
        self._logger = Logger("client")

        # Obtain config
        self.config = self._get_config()

        # Get ip and port
        address = self.config["destination_address"]
        port = self.config["port"]

        # Connect to the server
        self.Connect((address, port))

        # Create overlay instance later when additional settings have been received
        self.overlay = None
        self.additional_stats_settings = {'magicka_enabled': self.config['magicka_enabled'],
                                          'fatigue_enabled': self.config['fatigue_enabled']}

        self._logger.append("Client launched")

    """Network related functions"""

    def Network(self, data):
        pass

    # Log player succesfully connecting to the server socket
    def Network_socketConnect(self, data):
        self._logger.append("Successfully connected to the server")

    # Send player name upon connected event
    def Network_connected(self, data):
        self.Send_player_name()

    # Log received allies data
    # Save the data and update overlay
    def Network_receive_allies_data(self, data):
        self._logger.append("Received new allies data")
        player_data = data["allies_data"]
        self.overlay.update_frames(player_data)

    # Log receival of server's additional stats settings
    # Compare them with client's preferences and create Overlay instance with preferred settings (if available)
    def Network_receive_server_stats_settings(self, data):
        client_magicka_enabled = self.additional_stats_settings['magicka_enabled']
        client_fatigue_enabled = self.additional_stats_settings['fatigue_enabled']
        server_magicka_enabled = data['magicka_enabled']
        server_fatigue_enabled = data['fatigue_enabled']
        magicka_enabled = client_magicka_enabled and server_magicka_enabled
        fatigue_enabled = client_fatigue_enabled and server_fatigue_enabled

        self._logger.append("Received server stats settings (magicka and fatigue)")

        # Finally create overlay instance as the additional settings have been received
        self.overlay = Overlay(magicka_enabled, fatigue_enabled)

    # Log disconnected event
    # Close the client
    def Network_disconnected(self, data):
        if 'message' in data:
            self._logger.append("You have been disconnected " + data['message'])
        else:
            self._logger.append("You have been disconnected")
        sys.exit()

    # Pass the client's name to the server
    def Send_player_name(self):
        self.Send({"action": "receive_player_name", "player_name": self._get_player_name(), "ip": "127.0.0.1"})
        self._logger.append("Sending player name")

    """Helper functions"""

    # Load config from file
    def _get_config(self):
        try:
            with open("client_config.json") as config:
                return json.load(config)
        except Exception:
            self._logger.append(
                "Client config could not be loaded. Make sure there is client_config.json file in your directory.")

    # Get player's account name (tes3mp login) from config file
    def _get_player_name(self):
        return self.config["player_name"]


client = Client()
while 1:
    connection.Pump()
    client.Pump()

    if client.overlay is not None:
        client.overlay.root.update_idletasks()
        client.overlay.root.update()
