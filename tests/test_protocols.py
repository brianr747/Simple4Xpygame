from unittest import TestCase

from common.protocols import *


# We could speed this up by reusing the same Protocol object...
class TestProtocolInfo(TestCase):
    def test_BadFront(self):
        proto = Protocol()
        with self.assertRaises(UnsupportedMessage):
            proto.BuildMessage('SNort')

    def test_BuildMessage(self):
        proto = Protocol()
        self.assertEqual('?T|F|0', proto.BuildMessage('?T', False))

    def test_Build2(self):
        proto = Protocol()
        self.assertEqual('?T|T|0', proto.BuildMessage('?T', REPEAT=True))

    def test_Build3(self):
        proto = Protocol()
        self.assertEqual('?T|T|0', proto.BuildMessage('?T', REPEAT='T'))

    def test_Build4(self):
        proto = Protocol()
        with self.assertRaises(EncodingError):
            proto.BuildMessage('?T', REPEAT='X')

    def HandlerT(self, ID, repeat, step):
        self.was_called = True
        self.repeat = repeat
        self.step = step

    def test_handlemessage(self):
        proto = Protocol()
        self.was_called = False
        proto.Handlers['?T'] = self.HandlerT
        proto.HandleMessage('?T|T')
        self.assertTrue(self.was_called)
        self.assertTrue(self.repeat)
        self.assertEqual(0, self.step)




