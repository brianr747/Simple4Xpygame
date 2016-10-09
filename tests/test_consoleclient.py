from unittest import TestCase
import clients.consoleclient as consoleclient
from common.fleet import Fleet

class TestConsoleClient(TestCase):
    def test_Join(self):
        obj = consoleclient.ConsoleClient()
        obj.DoMock = True
        self.assertEqual(obj.State, 'Starting')
        obj.Join()
        self.assertEqual(obj.State, 'In Game')

    def test_MessageHandler_MT_fleet(self):
        obj = consoleclient.ConsoleClient()
        obj.FleetList = ["Dummy",]
        obj.MessageHandlerBase('FLEETS|')
        self.assertEqual(obj.FleetList, [])

    def test_MessageHandler_fleet(self):
        obj = consoleclient.ConsoleClient()
        f = Fleet(ID=0)
        f.x = 10.
        f.y = 10.
        obj.FleetList = ["Dummy", ]
        obj.MessageHandlerBase('FLEETS|'+f.ToString())
        self.assertEqual(len(obj.FleetList), 1)
        self.assertEqual(obj.FleetList[0].x, 10.)

