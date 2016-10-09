from common import mynetwork


class NetworkClient(mynetwork.SingleLineMasterClient):
    """
    NetworkClient
    Implements the network interface for the client. May be reused by other clients.

    Until we create a server stub, no unit test coverage possible.

    Clients need to:
    (1) Set MessageHandler to their game message handler.
    (2) Call Join()
    (3) Call DoNetwork() until State = 'In Game'
    (4)
    """

    def __init__(self):
        super(NetworkClient, self).__init__()
        self.State = "Lobby"
        self.PlayerNumber = None
        self.IsObserver = False
        self.FromServer = []
        self.ToServer = []
        self.MessageHandler = NetworkClient.DefaultMessageHandler

    @staticmethod
    def DefaultMessageHandler(msg):
        return

    def Join(self):
        self.network_events()
        if self.IsObserver:
            self.sendserver("Join-Observer")
            if self.PlayerNumber is None:
                self.PlayerNumber = 0
                self.sendserver("OBSERVE_AS=%i" % (self.PlayerNumber,))
                self.State = 'In Game'
        else:
            self.sendserver("?PLAYERS")
            self.State = "Joining"

    def handler_message(self, msg, fileno):
        if self.State == 'Joining':
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
                msg = msg.split(":")
                self.PlayerNumber = int(msg[1])
                self.State = "In Game"
            return
        if self.State == 'In Game':
            self.FromServer.append(msg)
            return
        raise NotImplementedError("Unknown client state!")

    @staticmethod
    def CleanMessage(p):
        if not type(p) == str:
            # No unicode?
            raise ValueError("Inputs must be strings")
        p.strip()
        if '\n' in p:
            raise ValueError("No \\n characters in messages!")
        return p

    def SendMessage(self, msg):
        self.ToServer.append(msg)

    def DoNetwork(self):
        """Call this to clear up all network tasks"""
        # Empty all outgoing messages
        self.network_events()
        for p in self.ToServer:
            p = NetworkClient.CleanMessage(p)
            self.sendserver(p)
        self.ToServer = []
        self.network_events()
        while len(self.FromServer) > 0:
            msg = self.FromServer.pop(0)
            self.MessageHandler(msg)


class MockNetworkClient(object):
    """
    MockNewtworkClient.py
    Substitute this over top of NetworkClient in unit tests.
    Could have made this inherit from the same class for object-oriented goodness,
    but this class is pretty lightweight, so the amount of duplicated code is small.
    """
    def __init__(self):
        self.State = "Lobby"
        self.PlayerNumber = None
        self.FromServer = []
        self.ToServer = []
        self.MessageHandler = NetworkClient.DefaultMessageHandler
        # Only appears in the mock; gives a complete list of all messages
        self.ProcessedToServer = []
        self.ProcessedFomServer = []
        # The SendMessageHandler provides a hook for the unit test framework to respond to messages
        self.SendMessageHandler =  NetworkClient.DefaultMessageHandler

    def Join(self):
        # We automatically connect (for now)
        self.State = "In Game"

    def SendMessage(self, msg):
        self.ToServer.append(msg)

    def DoNetwork(self):
        for p in self.ToServer:
            p = NetworkClient.CleanMessage(p)
            self.SendMessageHandler(p)
            self.ProcessedToServer.append(p)
        self.ToServer = []
        while len(self.FromServer) > 0:
            msg = self.FromServer.pop(0)
            self.ProcessedFomServer.append(msg)
            self.MessageHandler(msg)




