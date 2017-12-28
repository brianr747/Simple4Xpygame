"""
server_process.py

A ServerProcess will be the core class instantiated when a process starts up.

It can be run either in networked or non-networked mode.

In addition to a RealTimeServer, the ServerProcess will include RealTimeClient classes:
classes that are embedded in the same process thread. For example, AI players, and possibly
background simulation agents, could be embedded. Also, the non-networked mode will be used in
unit tests, academic simulations, and testing. The ServerProcess class handles all communication
between the RealTimeServer and RealTimeClients

The ServerProcessNetworked will open a network port, and allow ClientProcess network clients to
connect. The ClientProcess class will normally contain one RealTimeClient.

The base classes will not contain any particular simulation behaviour, they just handle the message passing.
"""

from real_time_server import RealTimeServer
from clients.real_time_client import RealTimeClient
from common import NormalTermination

class ServerProcess(object):
    def __init__(self):
        server =  RealTimeServer()
        # This line is technically not necessary, but it helps the PyCharm code introspection
        self.RealTimeServer = server
        self.SetServerObject(server)
        self.EmbeddedClients = {}
        # Start off at -1; first client is 0...
        self.MaxClientID = -1
        # Set this to None to keep running forever...
        self.MaxIterations = 1000

    def SetServerObject(self, obj):
        """
        Set the RealTimeServer object to be used
        :param obj: RealTimeServer
        :return:
        """
        self.RealTimeServer = obj
        # Override the stub for creating clients
        self.RealTimeServer.AddClientStub = self.AddEmbeddedClient

    def AddEmbeddedClient(self, client):
        """
        Add an embedded client.
        :param client: RealTimeClient
        :return: None
        """
        self.MaxClientID += 1
        self.EmbeddedClients[self.MaxClientID] = client

    def HandleCommunications(self):
        """
        Handle all the communication requests between the RealTimeServer and embedded clients.
        Ignores clients not in the embedded client list.
        :return:
        """
        # First, send messages to clients
        # Since not all messages may be processed here (they may be handled by networking),
        # need to create a holding queue.
        holding = []
        while len(self.RealTimeServer.MessagesOut) > 0:
            ID, msg = self.RealTimeServer.MessagesOut.pop(0)
            if ID not in self.EmbeddedClients:
                holding.append((ID, msg))
                continue
            # Is an embedded client
            client = self.EmbeddedClients[ID]
            # Client messages always go to/from server; no need for ID
            client.MessagesIn.append(msg)
        self.RealTimeServer.MessagesOut = holding
        if len(holding) > 0:
            self.RealTimeServer.Log('Unsent messages in server queue')
        # Next, handle incoming messages from embedded clients.
        for ID, client in self.EmbeddedClients.items():
            while len(client.MessagesOut) > 0:
                msg = client.MessagesOut.pop(0)
                self.RealTimeServer.MessagesIn.append((ID, msg))



    def ProcessStep(self):
        """
        Do one step for processing.
        :return:
        """
        self.HandleCommunications()
        # The server may blow us out with a termination
        self.RealTimeServer.Process()
        for client in self.EmbeddedClients.values():
            client.Process()


    def Run(self):
        """
        Run the loop until termination.
        Note: this is an infinite loop! Must ensure that we have a termination criterion
        :return:
        """
        cnt = 0
        while True:
            try:
                self.ProcessStep()
            except NormalTermination:
                return
            if self.MaxIterations is not None:
                cnt += 1
                if cnt >= self.MaxIterations:
                    raise ValueError('Hit maximum number of iterations!')
















