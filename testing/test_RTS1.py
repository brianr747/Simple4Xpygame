from __future__ import print_function

from clients.real_time_client import RealTimeClient
from common import NormalTermination
from common.event_queue import EventQueue as EventQueue
from server.server_process import ServerProcess
from server.real_time_server import RTS_BaseSimulation


# Build some simple clients

class Client1(RealTimeClient):
    def __init__(self, fin=100):
        super(Client1, self).__init__()
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
            self.MessagesOut.append('?T|REPEAT|2')
            return

    def ParseMessage(self, msg):
        print(msg)



def main():
    """
    Ad hoc testing...
    :return:
    """
    proc = ServerProcess()
    rts = RTS_BaseSimulation()
    rts.QuitTime = 10
    proc.SetServerObject(rts)
    c1 = Client1()
    c2 = Client1()
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



