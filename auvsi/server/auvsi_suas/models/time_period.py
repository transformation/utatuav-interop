class TimePeriod(object):
    """
    Describe a continuous period of time.
    A value of None indicates infinity. Both start and end are inclusive.
    """

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end

    def __eq__(self, other):
        """Two TimePeriods are equal if their attributes are equal."""
        if type(other) == type(self):
            return self.__dict__ == other.__dict__
        return False

    def within(self, time):
        """Returns true if time is within the TimePeriod."""
        return (self.start is None or time >= self.start) and \
                (self.end is None or time <= self.end)
