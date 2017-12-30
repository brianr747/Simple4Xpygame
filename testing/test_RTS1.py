from __future__ import print_function

from clients.real_time_client import RealTimeClient
from common import NormalTermination
from common.event_queue import EventQueue as EventQueue
from server.server_process import ServerProcess
from server.real_time_server import RTS_BaseEconomicSimulation
from clients.real_time_client import EconomicClient


# Build some simple clients

class Client1(RealTimeClient):
    def __init__(self, fin=100):
        super(Client1, self).__init__()
        self.TimeStepRequest = 2
        self.FinishTime = fin
        self.EventQueue = EventQueue()
        self.EventQueue.InsertEvent(-1, 'join')

        self.Time = -1

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
            self.MessagesOut.append('?T|REPEAT|{0}'.format(self.TimeStepRequest))
            return
        if event == 'sell':
            self.MessagesOut.append('!O|W1|cats|S|10|10')

    def ParseMessage(self, msg):
        """

        :param msg: str
        :return:
        """
        # print(msg)
        if msg.startswith('=T='):
            self.Time = int(msg[3:].strip())



class ManualClient(EconomicClient):
    def __init__(self):
        super(ManualClient, self).__init__()
        self.TimeStepRequest = 1
        self.LastTime = -2

    def Process(self):
        super(ManualClient, self).Process()
        if self.Time == self.LastTime:
            return
        print("STATE: T = {0}".format(self.Time))
        x = raw_input("Send > ")
        x = x.strip()
        if x.lower() == 'quit':
            raise KeyboardInterrupt('Dun!')
        if x.lower() == 's':
            print('State information')
            print('Time = ',self.Time)
            print('Exchanges\n===========')
            for name, ex in self.Exchanges.items():
                print(name, ex.Commodities.keys())
            print('Production Function')
            for k,v in self.Production.Techniques.items():
                print(k, v.Description, v.Output)

        if len(x) > 0:
            self.MessagesOut.append(x)
        else:
            self.LastTime = self.Time

    def ParseMessage(self, msg):
        print('Message received:', msg)
        super(ManualClient, self).ParseMessage(msg)



def main():
    """
    Ad hoc testing...
    :return:
    """
    proc = ServerProcess()
    rts = RTS_BaseEconomicSimulation()
    rts.CreateExchange('W1', 'Capital;Goods')
    rts.CreationInfo.append('INIT_BALANCE')
    rts.QuitTime = 10
    proc.SetServerObject(rts)
    c1 = Client1()
    c1.EventQueue.InsertEvent(2, 'sell')
    c2 = ManualClient()
    rts.ClientsToCreate = [c1, c2]
    rts.StartUp()
    try:
        proc.Run()
    except:
        print(rts.LogData)
        raise
    print(rts.LogData)


if __name__ == '__main__':
    main()



