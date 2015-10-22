"""UAS Telemetry model."""

from access_log import AccessLog
from aerial_position import AerialPosition
from takeoff_or_landing_event import TakeoffOrLandingEvent
from auvsi_suas.models.moving_obstacle import MovingObstacle
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from auvsi_suas.patches.simplekml_patch import AltitudeMode
from auvsi_suas.patches.simplekml_patch import Color


class UasTelemetry(AccessLog):
    """UAS telemetry reported by teams."""
    # The position of the UAS
    uas_position = models.ForeignKey(AerialPosition)
    # The heading of the UAS in degrees (e.g. 0=north, 90=east)
    uas_heading = models.FloatField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("UasTelemetry (pk:%s, user:%s, timestamp:%s, "
                       "heading:%s, pos:%s)" %
                       (str(self.pk), self.user.__unicode__(),
                        str(self.timestamp), str(self.uas_heading),
                        self.uas_position.__unicode__()))

    @classmethod
    def by_user(cls, user):
        """Gets the time-sorted list of access log for the given user.

        Note: This prefetches the related AerialPosition and GpsPosition
        for each entry.  Thus, any subsequent changes to those entries in
        the database after fetch may not be reflected in the objects.

        Args:
            user: The user to get the access log for.
        Returns:
            A list of access log objects for the given user sorted by timestamp.
        """
        # Almost every user of UasTelemetry.by_user wants to use
        # the related AerialPosition and GpsPosition.  To avoid excessive
        # database queries, we select these values from the database up front.
        return super(UasTelemetry, cls).by_user(user) \
                .select_related('uas_position__gps_position')

    @classmethod
    def dedupe(cls, logs):
        """Dedupes a set of UAS telemetry logs.

        For every set of sequential telemetry logs that are duplicates, it will
        filter all but the first log. Sensors and autopilots are unlikely to
        provide exactly the same data, even if the system is stationary, so
        logs which have exactly the same values are likely duplicates. Duplicate
        telemetry data is not allowed per the rules, so it is filtered.

        Args:
            logs: A sorted list of UasTelemetry logs.
        Returns:
            A list containing the non-duplicate logs in the original list.
        """
        # Check that logs were provided.
        if not logs:
            return logs

        # For each log, compare to previous. If different, add to output.
        filtered = []
        prev_log = None
        for log in logs:
            if prev_log is None or not prev_log.duplicate(log):
                # New unique log.
                filtered.append(log)
                prev_log = log

        return filtered

    def duplicate(self, other):
        """Determines whether this UasTelemetry is equivalent to another.

        This differs from the Django __eq__() method which simply compares
        primary keys. This method compares the field values.

        Args:
            other: The other log for comparison.
        Returns:
            True if they are equal.
        """
        return (self.uas_position.duplicate(other.uas_position) and
                self.uas_heading == other.uas_heading)

    def json(self):
        ret = {
            'id': self.pk,
            'user': self.user.pk,
            'timestamp': self.timestamp.isoformat(),
            'latitude': self.uas_position.gps_position.latitude,
            'longitude': self.uas_position.gps_position.longitude,
            'altitude_msl': self.uas_position.altitude_msl,
            'heading': self.uas_heading,
        }

        return ret

    @classmethod
    def kml(cls, user, logs, kml, kml_doc):
        """
        Appends kml nodes describing the given user's flight as described
        by the log array given.

        Args:
            user: A Django User to get username from
            logs: A list of UasTelemetry elements
            kml: A simpleKML Container to which the flight data will be added
            kml_doc: The simpleKML Document to which schemas will be added
        Returns:
            None
        """
        # KML Compliant Datetime Formatter
        kml_datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        icon = 'http://maps.google.com/mapfiles/kml/shapes/airports.png'
        threshold = 1  # Degrees

        kml_folder = kml.newfolder(name=user.username)

        flights = TakeoffOrLandingEvent.flights(user)
        if len(flights) == 0:
            return

        logs = filter(lambda log: cls._is_bad_position(log, threshold), logs)
        for i, flight in enumerate(flights):
            label = 'Flight {}'.format(i + 1)  # Flights are one-indexed
            kml_flight = kml_folder.newfolder(name=label)

            flight_logs = filter(lambda x: flight.within(x.timestamp), logs)
            if len(flight_logs) < 2:
                continue

            coords = []
            angles = []
            when = []
            for entry in flight_logs:
                pos = entry.uas_position.gps_position
                # Spatial Coordinates
                coord = (
                    pos.longitude, pos.latitude,
                    entry.uas_position.altitude_msl, )
                coords.append(coord)

                # Time Elements
                time = entry.timestamp.strftime(kml_datetime_format)
                when.append(time)

                # Degrees heading, tilt, and roll
                angle = (entry.uas_heading, 0.0, 0.0)
                angles.append(angle)

            # Create a new track in the folder
            trk = kml_flight.newgxtrack(name='Flight Path')
            trk.altitudemode = AltitudeMode.absolute

            # Append flight data
            trk.newwhen(when)
            trk.newgxcoord(coords)
            trk.newgxangle(angles)

            # Set styling
            trk.extrude = 1  # Extend path to ground
            trk.style.linestyle.width = 2
            trk.style.linestyle.color = Color.blue
            trk.iconstyle.icon.href = icon

            for obstacle in MovingObstacle.objects.all():
                obstacle.kml(path=flight_logs, kml=kml_flight, kml_doc=kml_doc)

    @classmethod
    def live_kml(cls, kml, timespan):
        users = User.objects.all()
        for user in users:
            period_logs = UasTelemetry.by_user(user)\
                .filter(timestamp__gt=timezone.now() - timespan)

            if len(period_logs) < 1:
                continue

            linestring = kml.newlinestring(name=user.username)
            coords = []
            for entry in period_logs:
                pos = entry.uas_position.gps_position
                # Spatial Coordinates
                coord = (
                    pos.longitude, pos.latitude,
                    entry.uas_position.altitude_msl, )
                coords.append(coord)
            linestring.coords = coords
            linestring.altitudemode = AltitudeMode.absolute
            linestring.extrude = 1
            linestring.style.linestyle.color = Color.blue
            linestring.style.polystyle.color = Color.changealphaint(100,
                                                                    Color.blue)

    @staticmethod
    def _is_bad_position(log, threshold):
        """
        Determine whether entry is not near latitude and longitude of 0,0.

        Args:
            x: UasTelemetry element
        Returns:
            Boolean: True if position is not near 0,0, else False
        """
        pos = log.uas_position.gps_position
        if max(abs(pos.latitude), abs(pos.longitude)) < threshold:
            return False
        return True
