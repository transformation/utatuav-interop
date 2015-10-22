import datetime
from auvsi_suas.models import TimePeriod
from django.test import TestCase
from django.utils import timezone


class TestTimePeriod(TestCase):
    """Tests the TimePeriod object."""

    def test_eq(self):
        """Tests TimePeriod equality."""
        # Self equality
        a = TimePeriod()
        self.assertEqual(a, a)

        # Two None objects
        a = TimePeriod()
        b = TimePeriod()
        self.assertEqual(a, b)

        # Same start (and end)
        a = TimePeriod(start=timezone.now())
        b = TimePeriod(start=a.start)
        self.assertEqual(a, b)

        # Same start, different end
        a = TimePeriod(start=timezone.now())
        b = TimePeriod(start=a.start, end=timezone.now())
        self.assertNotEqual(a, b)

        # Different start, same end
        a = TimePeriod(start=timezone.now(), end=timezone.now())
        b = TimePeriod(start=timezone.now(), end=a.end)
        self.assertNotEqual(a, b)

        # Different start, different end
        a = TimePeriod(start=timezone.now(), end=timezone.now())
        b = TimePeriod(start=timezone.now(), end=timezone.now())
        self.assertNotEqual(a, b)

    def test_within_standard(self):
        """Tests the within method with defined start and end."""
        t = TimePeriod(start=datetime.datetime(2000, 1, 1),
                       end=datetime.datetime(2001, 1, 1))

        # Clearly within
        self.assertTrue(t.within(datetime.datetime(2000, 6, 1)))

        # Inclusive start
        self.assertTrue(t.within(datetime.datetime(2000, 1, 1)))

        # Inclusive end
        self.assertTrue(t.within(datetime.datetime(2001, 1, 1)))

        # Not within below
        self.assertFalse(t.within(datetime.datetime(1999, 1, 1)))

        # Not within above
        self.assertFalse(t.within(datetime.datetime(2002, 1, 1)))

    def test_within_no_start(self):
        """Tests the within method with defined end and no start."""
        t = TimePeriod(end=datetime.datetime(2001, 1, 1))

        # Less than end
        self.assertTrue(t.within(datetime.datetime(2000, 6, 1)))

        # Inclusive end
        self.assertTrue(t.within(datetime.datetime(2001, 1, 1)))

        # Way below
        self.assertTrue(t.within(datetime.datetime(1999, 1, 1)))

        # Not within above
        self.assertFalse(t.within(datetime.datetime(2002, 1, 1)))

    def test_within_no_end(self):
        """Tests the within method with defined start and no end."""
        t = TimePeriod(start=datetime.datetime(2000, 1, 1))

        # Greater than start
        self.assertTrue(t.within(datetime.datetime(2000, 6, 1)))

        # Inclusive start
        self.assertTrue(t.within(datetime.datetime(2000, 1, 1)))

        # Not within below
        self.assertFalse(t.within(datetime.datetime(1999, 1, 1)))

        # Way above
        self.assertTrue(t.within(datetime.datetime(2002, 1, 1)))
