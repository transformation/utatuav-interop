"""Model for an access log."""

import datetime
import numpy as np
from time_period import TimePeriod
from django.conf import settings
from django.db import models
from django.utils import timezone


class AccessLog(models.Model):
    """Base class which logs access of information."""
    # Timestamp of the access
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    # The user which accessed the data
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("%s (pk:%s, user:%s, timestamp:%s)" %
                       (self.__class__.__name__, str(self.pk),
                        self.user.__unicode__(), str(self.timestamp)))

    @classmethod
    def by_user(cls, user):
        """Gets the time-sorted list of access log for the given user.

        Args:
            user: The user to get the access log for.
        Returns:
            A list of access log objects for the given user sorted by timestamp.
        """
        return cls.objects.filter(user_id=user.pk).order_by('timestamp')

    @classmethod
    def user_active(cls, user, base=None, delta=None):
        """Determines if a user is 'active'.

        A user is 'active' if they have reported telemetry since delta
        time in the past.

        Args:
            user: User to determine if is active
            base: Base time for active period, defaults to now
            delta: time period before base to consider user active
        Returns:
            True if user reported telemetry since base - delta
        """
        if base is None:
            base = timezone.now()
        if delta is None:
            delta = datetime.timedelta(seconds=10)

        since = base - delta

        return 0 != cls.by_user(user) \
            .filter(timestamp__gt=since) \
            .filter(timestamp__lt=base).count()

    @classmethod
    def by_time_period(cls, user, time_periods):
        """Gets a list of time-sorted lists of access logs for each time period.

        The method returns the full sets of AccessLogs for each TimePeriod. If
        overlapping TimePeriods are provided, the results may contain duplicate
        logs.

        Args:
            user: The user to get the access log for.
            time_periods: A list of TimePeriod objects.
        Returns:
            A list of AccessLog lists, where each AccessLog list contains all
            AccessLogs corresponding to the related TimePeriod.
        """
        ret = []

        for period in time_periods:
            logs = cls.by_user(user)

            if period.start:
                logs = logs.filter(timestamp__gte=period.start)
            if period.end:
                logs = logs.filter(timestamp__lte=period.end)

            ret.append(logs)

        return ret

    @classmethod
    def rates(cls, user, time_periods, time_period_logs=None):
        """Gets the access log rates.

        Args:
            user: The user to get the access log rates for.
            time_periods: A list of TimePeriod objects. Note: to avoid
                computing rates with duplicate logs, ensure that all
                time periods are non-overlapping.
            time_period_logs: Optional. A list of AccessLog lists, where each
                AccessLog list contains all AccessLogs corresponding to the
                related TimePeriod. If None, will obtain by calling
                by_time_period().
        Returns:
            A (max, avg) tuple. The max is the max time between logs, and avg
            is the avg time between logs.
            """
        # Check that time periods were provided.
        if not time_periods:
            return (None, None)

        # If logs were not provided, obtain.
        if not time_period_logs:
            time_period_logs = cls.by_time_period(user, time_periods)

        # Calculate time between log files.
        times_between_logs = []
        for i, period in enumerate(time_periods):
            # Get the logs for this period
            # Coerce the QuerySet into a list, so we can use negative indexing.
            logs = list(time_period_logs[i])

            # Account for a time period with no logs
            if len(logs) == 0:
                if period.start is not None and period.end is not None:
                    time_diff = (period.end - period.start).total_seconds()
                    times_between_logs.append(time_diff)
                continue

            # Account for time between takeoff and first log
            if period.start is not None:
                first = logs[0]
                time_diff = (first.timestamp - period.start).total_seconds()
                times_between_logs.append(time_diff)

            # Account for time between logs
            for j, log in enumerate(logs[:-1]):
                nextlog = logs[j + 1]
                time_diff = (nextlog.timestamp - log.timestamp).total_seconds()
                times_between_logs.append(time_diff)

            # Account for time between last log and landing
            if period.end is not None:
                last_log = logs[-1]
                time_diff = (period.end - last_log.timestamp).total_seconds()
                times_between_logs.append(time_diff)

        # Compute rates using the time between log files.
        times_between_logs = np.array(times_between_logs)
        times_between_max = np.max(times_between_logs)
        times_between_avg = np.mean(times_between_logs)
        return (times_between_max, times_between_avg)
