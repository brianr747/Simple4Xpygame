from unittest import TestCase
from common.event_queue import EventQueue as EventQueue

class TestEventQueue(TestCase):
    def test_InsertEvent(self):
        obj = EventQueue()
        obj.InsertEvent(-1, 'cat')
        self.assertEqual([(-1, 'cat')], obj.Events)
        obj.InsertEvent(-2, 'doggo')
        self.assertEqual([(-2, 'doggo'), (-1, 'cat')], obj.Events)
        self.assertEqual('doggo', obj.PopEvent(-2))
        self.assertEqual(None, obj.PopEvent(-2))
        self.assertEqual('cat', obj.PopEvent(10))
        self.assertEqual(None, obj.PopEvent(10))

