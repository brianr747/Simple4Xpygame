from unittest import TestCase
import clients.consoleclient as consoleclient

class TestConsoleClient(TestCase):
    def test_Join(self):
        obj = consoleclient.ConsoleClient()
        obj.DoMock = True
        self.assertEqual(obj.State, 'Starting')
        obj.Join()
        self.assertEqual(obj.State, 'In Game')

    def test_MessageHandler(self):
        self.fail()
