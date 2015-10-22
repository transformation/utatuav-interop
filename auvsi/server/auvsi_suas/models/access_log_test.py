"""Tests for the access_log module."""

import datetime
from auvsi_suas.models import AccessLog, TimePeriod
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone


class TestAccessLogCommon(TestCase):
    """Common code for AccessLog model tests."""

    def setUp(self):
        """Sets up the tests."""
        self.user1 = User.objects.create_user('user1', 'email@example.com',
                                              'pass')

        self.user2 = User.objects.create_user('user2', 'email@example.com',
                                              'pass')

        self.year2000 = datetime.datetime(2000, 1, 1, tzinfo=timezone.utc)
        self.year2001 = datetime.datetime(2001, 1, 1, tzinfo=timezone.utc)
        self.year2002 = datetime.datetime(2002, 1, 1, tzinfo=timezone.utc)
        self.year2003 = datetime.datetime(2003, 1, 1, tzinfo=timezone.utc)
        self.year2004 = datetime.datetime(2004, 1, 1, tzinfo=timezone.utc)

    def create_logs(self, user, num=10, start=None, delta=None):
        if start is None:
            start = timezone.now()
        if delta is None:
            delta = datetime.timedelta(seconds=1)

        logs = []

        for i in xrange(num):
            log = AccessLog(user=user)
            log.save()
            log.timestamp = start + i * delta
            log.save()
            logs.append(log)

        return logs


class TestAccessLogBasic(TestAccessLogCommon):
    """Tests the AccessLog model basic functionality."""

    def test_unicode(self):
        """Tests the unicode method executes."""
        log = AccessLog(timestamp=timezone.now(), user=self.user1)
        log.save()

        log.__unicode__()

    def test_no_data(self):
        logs = AccessLog.by_user(self.user1)
        self.assertEqual(len(logs), 0)

        logs = AccessLog.by_time_period(self.user1, [])
        self.assertEqual(len(logs), 0)

        log_rates = AccessLog.rates(self.user1, [])
        self.assertTupleEqual(log_rates, (None, None))

    def test_basic_access(self):
        logs = self.create_logs(self.user1)

        results = AccessLog.by_user(self.user1)
        self.assertSequenceEqual(logs, results)

    def test_multi_user(self):
        # Intersperse logs from two users
        logs = []
        for _ in xrange(10):
            logs += self.create_logs(self.user1, num=1)
            self.create_logs(self.user2, num=1)

        results = AccessLog.by_user(self.user1)
        self.assertSequenceEqual(logs, results)

    def test_user_active(self):
        delta = datetime.timedelta(seconds=1)

        self.create_logs(self.user1, start=self.year2000, num=10, delta=delta)

        latest_time = self.year2000 + 10 * delta

        # Active for user with recent logs
        self.assertTrue(AccessLog.user_active(self.user1, base=latest_time))

        # Not active for user with no logs
        self.assertFalse(AccessLog.user_active(self.user2, base=latest_time))

        # Not active for user with no recent logs
        self.assertFalse(AccessLog.user_active(self.user1, base=self.year2001))

        # Active now
        self.create_logs(self.user1, num=10, delta=delta)
        self.assertTrue(AccessLog.user_active(self.user1))


class TestAccessLogByTimePeriod(TestAccessLogCommon):
    """Test AccessLog.by_time_period()"""

    def setUp(self):
        super(TestAccessLogByTimePeriod, self).setUp()

        self.year2000_logs = self.create_logs(self.user1, start=self.year2000)
        self.year2003_logs = self.create_logs(self.user1, start=self.year2003)
        self.logs = self.year2000_logs + self.year2003_logs

    def to_lists(self, results):
        """Convert a list of QuerySet results to a list of lists."""
        return [list(r) for r in results]

    def test_single_period(self):
        """Single set of logs accessible."""
        results = AccessLog.by_time_period(self.user1, [
            TimePeriod(self.year2000, self.year2001)
        ])

        self.assertSequenceEqual([self.year2000_logs], self.to_lists(results))

    def test_full_range(self):
        """All logs from (-inf, inf)."""
        results = AccessLog.by_time_period(self.user1, [
            TimePeriod(None, None)
        ])

        self.assertSequenceEqual([self.logs], self.to_lists(results))

    def test_both_periods(self):
        """Both sets of logs, accesses individually."""
        results = AccessLog.by_time_period(self.user1, [
            TimePeriod(self.year2000, self.year2001),
            TimePeriod(self.year2003, self.year2004),
        ])

        self.assertSequenceEqual([self.year2000_logs, self.year2003_logs],
                                 self.to_lists(results))

    def test_non_intersecting_period(self):
        """No logs matched."""
        results = AccessLog.by_time_period(self.user1, [
            TimePeriod(self.year2001, self.year2002),
        ])

        self.assertSequenceEqual([[]], self.to_lists(results))

    def test_one_intersecting_period(self):
        """Only one period matches logs."""
        results = AccessLog.by_time_period(self.user1, [
            TimePeriod(self.year2001, self.year2002),
            TimePeriod(self.year2003, self.year2004),
        ])

        self.assertSequenceEqual([[], self.year2003_logs],
                                 self.to_lists(results))

    def test_open_start(self):
        """Logs (-inf, 2001)"""
        results = AccessLog.by_time_period(self.user1, [
            TimePeriod(None, self.year2001),
        ])

        self.assertSequenceEqual([self.year2000_logs], self.to_lists(results))

    def test_open_end(self):
        """Logs (2003, inf)"""
        results = AccessLog.by_time_period(self.user1, [
            TimePeriod(self.year2003, None),
        ])

        self.assertSequenceEqual([self.year2003_logs], self.to_lists(results))


class TestAccessLogRates(TestAccessLogCommon):
    """Test AccessLog.rates()"""

    def consistent_period(self, logs, delta):
        # rates() uses time between beginning/end of the period
        # and the first/last log to compute rates, so to get constant rates,
        # the period must begin and end delta seconds before/after the logs.
        return TimePeriod(logs[0].timestamp - delta,
                          logs[-1].timestamp + delta)

    def test_constant_rate(self):
        """Rates computed correctly."""
        delta = datetime.timedelta(seconds=1)

        logs = self.create_logs(self.user1, delta=delta)
        period = self.consistent_period(logs, delta)

        rates = AccessLog.rates(self.user1, [period])

        self.assertSequenceEqual((1, 1), rates)

    def test_provided_logs(self):
        """Rates computed with provided logs."""
        delta = datetime.timedelta(seconds=1)

        used_logs = self.create_logs(self.user1, delta=delta)
        unused_logs = self.create_logs(self.user1, delta=delta)
        period = self.consistent_period(used_logs, delta)

        rates = AccessLog.rates(self.user1, [period],
                                time_period_logs=[used_logs])

        self.assertSequenceEqual((1, 1), rates)

    def test_ignore_start_end(self):
        """When start and end are None, only times between logs are compared."""
        delta = datetime.timedelta(seconds=1)

        logs = self.create_logs(self.user1, delta=delta)
        period = TimePeriod(None, None)

        rates = AccessLog.rates(self.user1, [period])

        self.assertSequenceEqual((1, 1), rates)

    def test_multiple_periods(self):
        """Multiple periods are combined without introducing errors."""
        delta = datetime.timedelta(seconds=1)

        logs = [
            self.create_logs(self.user1,
                             start=self.year2000,
                             delta=delta),
            self.create_logs(self.user1,
                             start=self.year2001,
                             delta=delta),
        ]

        periods = [self.consistent_period(l, delta) for l in logs]

        rates = AccessLog.rates(self.user1, periods)

        self.assertSequenceEqual((1, 1), rates)

    def test_different_deltas(self):
        """Sets of logs are combined for overall rates."""
        delta = datetime.timedelta(seconds=1)

        logs = [
            self.create_logs(self.user1,
                             num=1000,
                             start=self.year2000,
                             delta=delta),
            self.create_logs(self.user1,
                             num=1000,
                             start=self.year2001,
                             delta=delta / 2),
        ]

        periods = [self.consistent_period(l, delta) for l in logs]

        rates = AccessLog.rates(self.user1, periods)

        self.assertAlmostEqual(1.0, rates[0])  # max
        self.assertAlmostEqual(0.75, rates[1], delta=0.001)  # avg
