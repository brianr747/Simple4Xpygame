from __future__ import print_function

from unittest import TestCase

from clients.real_time_client import RealTimeClient
from server.real_time_server import RTS_BaseSimulation
from server.server_process import ServerProcess
from common.event_queue import EventQueue as EventQueue


class TestRTS_BaseSimulation(TestCase):
    def test_setup(self):
        proc = ServerProcess()
        rts = RTS_BaseSimulation()
        proc.SetServerObject(rts)
        rts.ClientsToCreate.append(RealTimeClient)
        rts.StartUp()
        self.assertEqual(1, rts.NumPlayers)
        self.assertEqual(1, len(proc.EmbeddedClients))






