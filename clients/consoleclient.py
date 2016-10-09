"""
consoleclient.py

This implements a player client, but with a console interface for the human playing.
This allows us to test new game commands, without requiring a graphical interface.

The player can use a graphical observer client to aid play.


Copyright 2016 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from common import mynetwork


class ClientNetwork(mynetwork.SingleLineMasterClient):
    """
    ClientNetwork
    Implements the network interface for the client. May be reused by other clients.

    Until we create a server stub, no unit test coverage possible.
    """

    def __init__(self):
        super(ClientNetwork, self).__init__()
        self.State = "Lobby"
        self.PlayerNumber = None
        self.FromServer = []
        self.ToServer = []

    def network_events(self):
        super(self, ClientNetwork).network_events()

    def Join(self):
        self.sendserver("?PLAYERS")
        self.State = "Joining"

    def handler_message(self, msg, fileno):
        if self.State == 'JOINING':
            if msg.startswith("PLAYERS,"):
                msg = msg.split(",")
                # Remove first entry = "PLAYERS,"
                msg.pop(0)
                player_connected = [x == "True" for x in msg]
                # print player_connected
                if False not in player_connected:
                    raise ValueError("Too many players")
                response = ""
                for i in range(0, len(player_connected)):
                    if not player_connected[i]:
                        response = "JOIN-%i" % (i,)
                        self.sendserver(response)
                        return
            if msg.startswith('CONNECTED:'):
                msg = msg.split("=")
                self.PlayerNumber = int(msg[1])
                self.State = "In Game"
            return
        if self.State == 'In Game':
            self.FromServer.append(msg)
            return

    def DoNetwork(self):
        """Call this to clear up all network tasks"""
        # Empty all outgoing messages
        for p in self.ToServer:
            if not type(p) == str:
                # No unicode?
                raise ValueError("Inputs must be strings")
            p.strip()
            if '\n' in p:
                raise ValueError("No \\n characters in messages!")
            self.sendserver(p)
        self.ToServer = []
        self.network_events()
