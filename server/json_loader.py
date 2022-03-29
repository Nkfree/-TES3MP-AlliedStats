import json
import sys
from json import JSONDecodeError

from logger import Logger


class JsonLoader:

    def __init__(self, logger: Logger):
        self._logger = logger
        self.config = self._get_config()
        self._player_data = None

    def get_player_data_by_name(self, player_name: str):
        if player_name in self._player_data:
            return self._player_data[player_name]
        return None

    def get_tes3mp_ip_by_name(self, player_name: str):
        if player_name in self._player_data:
            return self._player_data[player_name]["ip"]
        return None

    def load_player_data(self):

        # Try loading the .json with player names and allies data for each of the player"s allies
        try:
            with open(self._get_file_path()) as data:
                try:
                    new_data = json.load(data)
                    old_data = self._player_data

                    if isinstance(new_data, list):
                        new_data = dict(new_data)

                    if new_data != old_data:
                        self._player_data = new_data
                        return
                except JSONDecodeError:
                    print("JSONDecodeError: Decoding failed as the file is probably being worked with" +
                          "-the process of tes3mp lua updating .json file - this is expected behaviour and " +
                          "nothing to be worry about")


        except Exception:
            self._logger.append("Opening .json file failed. Make sure the path provided in your config directs" +
                                " to the absolute path of the alliesHealthBars.json file located in " +
                                "server/data/ by default.")
            sys.exit()

    # Get server config
    def _get_config(self):
        try:
            with open("server_config.json") as config:
                return json.load(config)
        except Exception:
            self._logger.append(
                "Server config could not be loaded. Make sure there is server_config.json file in your directory.")

    # Get absolute file path of the .json containing player names and related health data
    def _get_file_path(self):
        return self.config["file_path"]

    def get_stats_settings(self):
        return {"magicka_enabled": self.config["magicka_enabled"], "fatigue_enabled": self.config["fatigue_enabled"]}
