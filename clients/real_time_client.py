"""
real_time_client.py

The RealTimeClient class contains the code that manages a client. It may be embedded in a ServerProces.

If we want a stand-alone client, we embed it in a ClientProcess.

The holding classes manage all communications for the client.
"""


from common.event_queue import EventQueue
from common.exchange import Exchange
from common.production import Production
from common.protocols import Protocol

class RealTimeClient(object):
    def __init__(self):
        self.MessagesIn = []
        self.MessagesOut = []

    def Process(self):
        pass


class EconomicClient(RealTimeClient):
    def __init__(self, fin=100):
        super(EconomicClient, self).__init__()
        self.TimeStepRequest = 2
        self.FinishTime = fin
        self.EventQueue = EventQueue()
        self.EventQueue.InsertEvent(-1, 'join')
        self.Time = -1
        self.Exchanges = {}
        # Turn BuildState to False to disable automatic state building.
        self.BuildState = True
        self.EventQueue.InsertEvent(0, 'build_state')
        self.Production = Production()
        self.Protocol = Protocol()

    def Process(self):
        if len(self.MessagesIn) > 0:
            msg = self.MessagesIn.pop(0)
            self.ParseMessage(msg)
            return
        event = self.EventQueue.PopEvent(self.Time)
        # Only do one event in each Process() step (to play nice...)
        if event is None:
            return
        if event == 'join':
            self.MessagesOut.append('!JOIN_PLAYER')
            msg = self.Protocol.BuildMessage('?T', repeat=True, step=self.TimeStepRequest)
            self.MessagesOut.append(msg)
            return
        if event == 'build_state' and self.BuildState:
            self.MessagesOut.append('?W')
            self.MessagesOut.append('?P')


    def ParseMessage(self, msg):
        """

        :param msg: str
        :return:
        """
        # print(msg)
        if msg.startswith('=T|'):
            self.Time = int(msg[3:].strip())
        if msg.startswith('=P='):
            self.Production.ParseTemplate(msg[3:].strip())
        if msg.startswith('=W'):
            info = msg.split('|')
            if info[0] == '=W':
                for n in info[1:]:
                    self.MessagesOut.append('?W1|' + n)
            elif info[1] == '=W1':
                if not info[0].startswith('=W='):
                    raise ValueError('unparsable server response: ' + msg)
                name = info[0][3:]
                template = '|'.join(info[1:])
                self.Exchanges[name] = Exchange(template_str=template)

