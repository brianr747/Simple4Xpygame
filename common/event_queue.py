"""
event_queue.py
The EventQueue object implements an event queue with a time index.
"""


class EventQueue(object):
    def __init__(self):
        self.Events = []

    def InsertEvent(self, index, event):
        """

        :param index: int
        :param event: object
        :return:
        """
        for pos in range(0, len(self.Events)):
            if index < self.Events[pos][0]:
                self.Events.insert(pos, (index, event))
                return
        self.Events.append((index, event))

    def PopEvent(self, index):
        """
        Get the first event with event index <= index
        Returns None if no such event exists.
        :param index: int
        :return: object
        """
        if len(self.Events) > 0:
            if self.Events[0][0] <= index:
                dummy = self.Events.pop(0)
                return dummy[1]
        return None