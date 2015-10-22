"""Takeoff or landing event model."""

from access_log import AccessLog
from time_period import TimePeriod
from django.db import models
from django.utils import timezone


class TakeoffOrLandingEvent(AccessLog):
    """Marker for a UAS takeoff/landing. UAS must interop during that time."""
    # Whether the UAS is now in the air
    uas_in_air = models.BooleanField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode('TakeoffOrLandingEvent (pk%s, user:%s, timestamp:%s, '
                       'uas_in_air:%s)' %
                       (str(self.pk), self.user.__unicode__(),
                        str(self.timestamp), str(self.uas_in_air)))

    @classmethod
    def flights(cls, user):
        """Gets the time periods for which the given user was in flight.

        Duplicate takeoff or landing events are ignored.

        Args:
            user: The user for which to get flight periods for.
        Returns:
            A list of TimePeriod objects corresponding to individual flights.
        """
        # Get the access logs for the user
        access_logs = TakeoffOrLandingEvent.by_user(user)

        time_periods = []

        # If UAS landing at start, assume forgot to log takeoff, assign infinity
        if len(access_logs) > 0 and not access_logs[0].uas_in_air:
            time_periods.append(TimePeriod(None, access_logs[0].timestamp))

        # Use transition from ground to air and air to ground for flight periods
        takeoff_time = None
        landing_time = None
        uas_in_air = False
        for log in access_logs:
            # Check for transition from ground to air
            if not uas_in_air and log.uas_in_air:
                takeoff_time = log.timestamp
                uas_in_air = log.uas_in_air
            # Check for transition from air to ground
            if uas_in_air and not log.uas_in_air:
                landing_time = log.timestamp
                uas_in_air = log.uas_in_air

                time_periods.append(TimePeriod(takeoff_time, landing_time))

        # If UAS in air at end, assume forgot to log landing, assign infinity
        if uas_in_air:
            time_periods.append(TimePeriod(access_logs.last().timestamp, None))

        return time_periods

    @classmethod
    def user_in_air(cls, user, time=None):
        """Determine if given user is currently in-air

        Args:
            user: User to get in-flight status for
            time: Time to check in-air status; default now
        Returns:
            True if user is currently in-flight, False otherwise
        """
        if time is None:
            time = timezone.now()

        event = cls.objects \
            .filter(user=user.pk) \
            .filter(timestamp__lt=time) \
            .order_by('timestamp') \
            .last()

        if event:
            return event.uas_in_air
        else:
            return False
