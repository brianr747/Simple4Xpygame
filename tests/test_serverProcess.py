from unittest import TestCase

from clients.real_time_client import RealTimeClient
from common import NormalTermination
from server.server_process import ServerProcess


class TestServerProcess(TestCase):
    def test_AddEmbeddedClient(self):
        proc = ServerProcess()
        obj = RealTimeClient()
        proc.AddEmbeddedClient(obj)
        self.assertEqual(0, proc.MaxClientID)

    def test_HandleCommunications_1(self):
        proc = ServerProcess()
        obj = RealTimeClient()
        proc.AddEmbeddedClient(obj)
        proc.RealTimeServer.SendMessage("test", 0)
        self.assertEqual(1, len(proc.RealTimeServer.MessagesOut))
        proc.HandleCommunications()
        self.assertEqual([], proc.RealTimeServer.MessagesOut)
        self.assertEqual(['test'], obj.MessagesIn)
        # Pass #2: send another message to the client, and then to a non-existent one.
        proc.RealTimeServer.SendMessage("test2", 0)
        proc.RealTimeServer.SendMessage("test3", 1)
        proc.HandleCommunications()
        # The second message should be the only one left in the queue.
        self.assertEqual([(1, 'test3')], proc.RealTimeServer.MessagesOut)
        # The client should now have two messages
        self.assertEqual(['test', 'test2'], obj.MessagesIn)

    def test_HandleCommunications_2(self):
        proc = ServerProcess()
        obj1 = RealTimeClient()
        obj2 = RealTimeClient()
        proc.AddEmbeddedClient(obj1)
        proc.AddEmbeddedClient(obj2)
        proc.RealTimeServer.SendMessage("test", 0)
        proc.RealTimeServer.SendMessage("test2", 1)
        obj1.MessagesOut.append('obj1')
        obj2.MessagesOut.append('obj2-1')
        obj2.MessagesOut.append('obj2-2')
        proc.HandleCommunications()
        self.assertEqual(obj1.MessagesIn, ['test'])
        self.assertEqual(obj2.MessagesIn, ['test2'])
        self.assertEqual(3, len(proc.RealTimeServer.MessagesIn))
        self.assertIn((0, 'obj1'), proc.RealTimeServer.MessagesIn)
        self.assertIn((1, 'obj2-1'), proc.RealTimeServer.MessagesIn)
        self.assertIn((1, 'obj2-2'), proc.RealTimeServer.MessagesIn)


    def test_CreateClient(self):
        proc = ServerProcess()
        proc.RealTimeServer.CreateClient('')
        self.assertEqual(1, len(proc.EmbeddedClients))

    def test_process_step(self):
        proc = ServerProcess()
        with self.assertRaises(NormalTermination):
            proc.ProcessStep()

