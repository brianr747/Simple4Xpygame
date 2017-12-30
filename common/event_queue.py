"""
event_queue.py
The EventQueue object implements an event queue with a time index.
"""


class Event(object):
    """
    Event object: Handle callbacks as events
    """
    def __init__(self, callback=None, f_args=(), kwargs=None, txt = '', repeat=None, start_repeat=0):
        """
        If repeat is not None, the event automatically repeats every "repeat" steps, starting at "start_repeat"
        :param callback: function
        :param f_args: list
        :param kwargs: dict
        :param txt: str
        :param repeat: int
        :param start_repeat: int
        """
        self.CallBack = callback
        self.Args = f_args
        self.Kwargs = kwargs
        self.Text = txt
        self.Repeat = repeat
        self.StartRepeat = start_repeat

    def Evaluate(self):
        if self.CallBack is None:
            raise ValueError('Event callback not set:')
        if self.Kwargs is None:
            self.CallBack(*self.Args)
        else:
            self.CallBack(*self.Args, **self.Kwargs)



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
                dummy, event = self.Events.pop(0)
                if type(event) == Event:
                    if event.Repeat is not None:
                        # Do not allow a Repeat of zero!
                        event.Repeat = min(1, event.Repeat)
                        # If it repeats, re-insert the event at "StartRepeat" + "Repeat"
                        new_index = event.StartRepeat + event.Repeat
                        event.StartRepeat = new_index
                        self.InsertEvent(new_index, event)
                return event
        return None