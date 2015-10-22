"""Tests for the uas_telemetry module."""

import iso8601
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.models import UasTelemetry
import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from simplekml import Kml


class TestUasTelemetryBase(TestCase):
    """Base for the UasTelemetry tests."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'testemail@x.com',
                                             'testpass')
        self.user.save()

    def create_log_element(self, timestamp, user, lat, lon, alt, heading):
        pos = GpsPosition(latitude=lat, longitude=lon)
        pos.save()
        apos = AerialPosition(gps_position=pos, altitude_msl=alt)
        apos.save()
        log = UasTelemetry(timestamp=timezone.now(),
                           user=user,
                           uas_position=apos,
                           uas_heading=heading)
        log.save()
        return log


class TestUasTelemetry(TestUasTelemetryBase):
    """Tests the UasTelemetry model."""

    def setUp(self):
        super(TestUasTelemetry, self).setUp()

        self.log = self.create_log_element(
            timestamp=timezone.now(),
            user=self.user,
            lat=10,
            lon=100,
            alt=200,
            heading=90)

    def test_unicode(self):
        """Tests the unicode method executes."""
        self.assertTrue(self.log.__unicode__())

    def test_duplicate_unequal(self):
        """Tests duplicate function with unequal telemetry."""
        log1 = self.create_log_element(
            timestamp=timezone.now(),
            user=self.user,
            lat=20,
            lon=200,
            alt=200,
            heading=90)
        log2 = self.create_log_element(
            timestamp=timezone.now(),
            user=self.user,
            lat=10,
            lon=100,
            alt=300,
            heading=90)
        log3 = self.create_log_element(
            timestamp=timezone.now(),
            user=self.user,
            lat=10,
            lon=100,
            alt=200,
            heading=10)

        self.assertFalse(self.log.duplicate(log1))
        self.assertFalse(self.log.duplicate(log2))
        self.assertFalse(self.log.duplicate(log3))

    def test_duplicate_equal(self):
        """Tests duplicate function with equal telemetry."""
        log1 = self.create_log_element(
            timestamp=timezone.now(),
            user=self.user,
            lat=10,
            lon=100,
            alt=200,
            heading=90)

        self.assertTrue(self.log.duplicate(self.log))
        self.assertTrue(self.log.duplicate(log1))

    def test_json(self):
        """Tests JSON-style output."""
        data = self.log.json()

        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('timestamp', data)
        self.assertIn('latitude', data)
        self.assertIn('longitude', data)
        self.assertIn('altitude_msl', data)
        self.assertIn('heading', data)

        # Timestamp is valid ISO 8601, with timezone
        iso8601.parse_date(data['timestamp'])

        self.assertEqual(10, data['latitude'])
        self.assertEqual(100, data['longitude'])
        self.assertEqual(200, data['altitude_msl'])
        self.assertEqual(90, data['heading'])


class TestUasTelemetryDedupe(TestUasTelemetryBase):
    def setUp(self):
        super(TestUasTelemetryDedupe, self).setUp()

        self.log1 = self.create_log_element(
            timestamp=timezone.now(),
            user=self.user,
            lat=10,
            lon=200,
            alt=200,
            heading=90)
        self.log2 = self.create_log_element(
            timestamp=timezone.now(),
            user=self.user,
            lat=20,
            lon=200,
            alt=200,
            heading=90)
        self.log3 = self.create_log_element(
            timestamp=timezone.now(),
            user=self.user,
            lat=30,
            lon=200,
            alt=200,
            heading=90)
        self.log4 = self.create_log_element(
            timestamp=timezone.now(),
            user=self.user,
            lat=40,
            lon=200,
            alt=200,
            heading=90)

    def test_no_logs(self):
        """Tests empty log."""
        self.assertEqual(UasTelemetry.dedupe([]), [])

    def test_no_duplicates(self):
        """Tests no duplicates in list."""
        orig = [self.log1, self.log2, self.log3, self.log4]
        self.assertEqual(UasTelemetry.dedupe(orig), orig)

    def test_boundary_duplicates(self):
        """Tests duplicates on the bounds of the list."""
        orig = [self.log1, self.log1, self.log2, self.log2, self.log2]
        expect = [self.log1, self.log2]
        self.assertEqual(UasTelemetry.dedupe(orig), expect)

    def test_duplicates(self):
        orig = [self.log1, self.log1, self.log2, self.log3, self.log3,
                self.log4, self.log4]
        expect = [self.log1, self.log2, self.log3, self.log4]
        self.assertEqual(UasTelemetry.dedupe(orig), expect)


class TestUasTelemetryKML(TestUasTelemetryBase):
    # String formatter for KML format that expects lon, lat, alt arguments
    coord_format = '<gx:coord>{} {} {}</gx:coord>'

    def create_log_element(self, lat, lon, alt):
        """Override to define defaults."""
        super(TestUasTelemetryKML, self).create_log_element(
            timestamp=timezone.now(),
            user=self.user,
            lat=lat,
            lon=lon,
            alt=alt,
            heading=80)

    def test_kml_simple(self):
        coordinates = [
            (-76.0, 38.0, 0.0),
            (-76.0, 38.0, 10.0),
            (-76.0, 38.0, 20.0),
            (-76.0, 38.0, 30.0),
            (-76.0, 38.0, 100.0),
            (-76.0, 38.0, 30.0),
            (-76.0, 38.0, 60.0),
        ]
        # Create Coordinates
        start = TakeoffOrLandingEvent(user=self.user, uas_in_air=True)
        start.save()
        for coord in coordinates:
            self.create_log_element(*coord)
        end = TakeoffOrLandingEvent(user=self.user, uas_in_air=False)
        end.save()

        kml = Kml()
        UasTelemetry.kml(
            user=self.user,
            logs=UasTelemetry.by_user(self.user),
            kml=kml,
            kml_doc=kml, )
        for coord in coordinates:
            tag = self.coord_format.format(coord[1], coord[0], coord[2])
            self.assertTrue(tag in kml.kml())

    def test_kml_empty(self):
        kml = Kml()
        UasTelemetry.kml(
            user=self.user,
            logs=UasTelemetry.by_user(self.user),
            kml=kml,
            kml_doc=kml, )

    def test_kml_filter(self):
        coordinates = [
            (-76.0, 38.0, 0.0),
            (-76.0, 38.0, 10.0),
            (-76.0, 38.0, 20.0),
            (-76.0, 38.0, 30.0),
            (-76.0, 38.0, 100.0),
            (-76.0, 38.0, 30.0),
            (-76.0, 38.0, 60.0),
        ]
        filtered_out = [(0.1, 0.001, 100), (0.0, 0.0, 0)]
        # Create Coordinates
        start = TakeoffOrLandingEvent(user=self.user, uas_in_air=True)
        start.save()
        for coord in coordinates:
            self.create_log_element(*coord)
        for coord in filtered_out:
            self.create_log_element(*coord)
        end = TakeoffOrLandingEvent(user=self.user, uas_in_air=False)
        end.save()

        kml = Kml()
        UasTelemetry.kml(
            user=self.user,
            logs=UasTelemetry.by_user(self.user),
            kml=kml,
            kml_doc=kml, )

        for filtered in filtered_out:
            tag = self.coord_format.format(filtered[1], filtered[0],
                                           filtered[2])
            self.assertTrue(tag not in kml.kml())

        for coord in coordinates:
            tag = self.coord_format.format(coord[1], coord[0], coord[2])
            self.assertTrue(tag in kml.kml())
