from time import sleep
from weakref import WeakKeyDictionary
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from json_loader import JsonLoader
from logger import Logger

"""All methods starting with capital letter are network related"""


class ClientChannel(Channel):

    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

        self._ip = None
        self._tes3mp_ip = None
        self._awaiting_tes3mp_ip = True
        self._player_name = None
        self._allies_data = dict()
        self._has_update = False

    def Network(self, data):
        pass

    def Network_receive_player_name(self, data):
        self.player_name = data["player_name"]

        server.logger.append("Received player name: " + self.player_name + " from client with ip " + self.ip)

    # Define explicit method for kicking
    def Kick(self, message: str):
        self.Close(message)

    def Close(self, message: str = None):
        # Let client know first
        data = {"action": "disconnected"}
        player = self.player_name

        if not player:
            player = self.ip

        if message is not None:
            data["message"] = message
            server.logger.append("Player " + player + " has been kicked. Reason: " + message)
        else:
            server.logger.append("Player " + player + " has disconnected.")

        self.Send(data)

        # Remove client entry and close the connection for them
        del self.server.clients[self]
        self.close()

    @property
    def player_name(self):
        return self._player_name

    @player_name.setter
    def player_name(self, value):
        self._player_name = value

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, value):
        self._ip = value

    @property
    def tes3mp_ip(self):
        return self._tes3mp_ip

    @tes3mp_ip.setter
    def tes3mp_ip(self, value):
        self._tes3mp_ip = value

    @property
    def awaiting_tes3mp_ip(self):
        return self._awaiting_tes3mp_ip

    @awaiting_tes3mp_ip.setter
    def awaiting_tes3mp_ip(self, value):
        self._awaiting_tes3mp_ip = value

    @property
    def allies_data(self):
        return self._allies_data

    @allies_data.setter
    def allies_data(self, value):
        self._allies_data = value

    @property
    def has_update(self):
        return self._has_update

    @has_update.setter
    def has_update(self, value):
        self._has_update = value

    @property
    def server(self):
        return self._server


class MyServer(Server):
    channelClass = ClientChannel

    def __init__(self, log_prefix_file_name: str):
        # Create instance of JsonLoader that will load server config and the player"s allies data
        self.logger = Logger(log_prefix_file_name)
        self.json_loader = JsonLoader(self.logger)

        # Set server address, port and launch the server
        address = self.json_loader.config["local_address"]
        port = self.json_loader.config["port"]
        Server.__init__(self, localaddr=(address, port))
        self.logger.append("Server launched")

        self.stats_settings = self.json_loader.get_stats_settings()

        # Clients, their ip addresses and player names go here
        self.clients = WeakKeyDictionary()

    def Connected(self, client, address):
        self.logger.append("New connection: " + str(client))
        self.Add_client(client)
        client.ip = address[0]

        # Send additional stats data to client
        self.Send_server_stats_settings(client)

    def Add_client(self, client):
        self.clients[client] = True

    def Send_allies_data(self, client):
        allies_data = client.allies_data
        data = {"action": "receive_allies_data", "allies_data": allies_data}
        client.Send(data)
        client.has_update = False

    def Send_server_stats_settings(self, client):
        data = {"action": "receive_server_stats_settings",
                "magicka_enabled": self.stats_settings["magicka_enabled"],
                "fatigue_enabled": self.stats_settings["fatigue_enabled"]}
        client.Send(data)

    def has_name(self, client):
        return client.player_name is not None

    def has_update(self, client):
        return client.has_update is True

    def reset_has_update(self):
        for client in self.clients:
            client.has_update = False

    # Update player data for client iif they differ from last obtained
    def update_allies_data(self, client, new_data):
        old_data = client.allies_data

        if new_data == old_data:
            return

        self.logger.append("Updated " + client.player_name + "'s allies data")
        client.allies_data = new_data
        client.has_update = True

    # Update tes3mp ip of clients who are awaiting it
    # Also validate client"s ips to filter out those trying to impersonate other players
    def update_clients_awaiting_tes3mp_ip(self):
        clients = self.get_clients_awaiting_tes3mp_ip()
        for client in clients:
            if client.player_name is not None:
                tes3mp_ip = self.json_loader.get_tes3mp_ip_by_name(client.player_name)
                if tes3mp_ip:
                    client.tes3mp_ip = tes3mp_ip
                    # Disable client awaiting tes3mp ip
                    client.awaiting_tes3mp_ip = False
                    # Validate client's ips
                    self.validate_client(client)

    # Update clients" allies data if the data is new
    def update_clients_allies_data(self):
        clients = self.get_clients_without_update()
        for client in clients:
            new_data = self.json_loader.get_player_data_by_name(client.player_name)
            if new_data:
                self.update_allies_data(client, new_data["alliesData"])

    # Send data to clients having update
    def update_clients_having_update(self):
        clients = self.get_clients_having_update()
        for client in clients:
            self.logger.append("Sending allies data to " + client.player_name)
            self.Send_allies_data(client)
            # Reset has_update flag for the client
            client.has_update = False


    # Get clients waiting for tes3mp ip in order to check for impersonation
    def get_clients_awaiting_tes3mp_ip(self):
        return [client for client in self.clients if client.awaiting_tes3mp_ip]

    # Get clients awaiting new data
    def get_clients_without_update(self):
        return [client for client in self.clients if not client.has_update and not client.awaiting_tes3mp_ip]

    def get_clients_having_update(self):
        return [client for client in self.clients if client.has_update]

    def validate_client(self, client):
        if client.ip != client.tes3mp_ip:
            client.Kick("Tried impersonating another player.")
            return
        self.logger.append("Player " + client.player_name + " has been successfully verified")



server = MyServer("server")

while True:
    # Get players' data output from server first
    server.json_loader.load_player_data()

    # Update and validate tes3mp ip addresses for clients
    server.update_clients_awaiting_tes3mp_ip()

    # Update clients with allies data if there is any for them
    server.update_clients_allies_data()

    # If the clients have received new data their has_update flags will be turned on
    # Issue an update for these clients
    server.update_clients_having_update()

    server.Pump()
    sleep(0.01)
