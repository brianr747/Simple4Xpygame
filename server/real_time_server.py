"""
real_time_server.py

The RealTimeServer class holds the object that manages the server. It is embedded in a ServerProcess.

Despite the name, there are no communications handled in the class; that is the job of the ServerProcess.

This allows the server code to treat all RealTimeClients equally, whether or not they are embedded in
the server process.
"""


import clients.real_time_client
from common import NormalTermination

class RealTimeServer(object):
    def __init__(self):
        self.MessagesOut = []
        self.MessagesIn = []

    def SendMessage(self, msg, id_client):
        self.MessagesOut.append((id_client, msg))

    def CreateClient(self, msg):
        """
        Create an embedded client, based on a message.
        The base class always creates a RealTimeClient (which does nothing;)
        subclasses will create appropriate classes.

        :param msg: str
        :return:
        """
        obj = clients.real_time_client.RealTimeClient()
        self.AddClientStub(obj)

    def AddClientStub(self, obj):
        """
        Stub that is overridden by the ServerProcess class.
        :param obj: clients.real_time_client.RealTimeClient
        :return: None
        """
        pass

    def Process(self):
        """
        Base class just terminates the thing...
        :return:
        """
        raise NormalTermination('Dun!')


class RTS_BaseSimulation(RealTimeServer):
    """
    A base simulation class.
    """

    def __init__(self):
        super(RTS_BaseSimulation, self).__init__()
        self.ClientsToCreate = []
        self.T = -1
        self.NumPlayers = 0

    def StartUp(self):
        self.NumPlayers = len(self.ClientsToCreate)
        for client in self.ClientsToCreate:
            self.AddClientStub(client)


