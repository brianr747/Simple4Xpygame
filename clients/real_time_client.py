"""
real_time_client.py

The RealTimeClient class contains the code that manages a client. It may be embedded in a ServerProces.

If we want a stand-alone client, we embed it in a ClientProcess.

The holding classes manage all communications for the client.
"""



class RealTimeClient(object):
    def __init__(self):
        self.MessagesIn = []
        self.MessagesOut = []

    def Process(self):
        pass