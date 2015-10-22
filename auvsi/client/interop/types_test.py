import unittest

from . import Telemetry, StationaryObstacle, MovingObstacle


class TestTelemetry(unittest.TestCase):
    """Test the Telemetry object. There is very little to see here."""

    def test_valid(self):
        """Test valid inputs"""
        # No exceptions
        Telemetry(latitude=38, longitude=-76, altitude_msl=100, uas_heading=90)

    def test_invalid(self):
        """Test invalid inputs"""
        # Bad latitude
        with self.assertRaises(ValueError):
            Telemetry(latitude=120,
                      longitude=-76,
                      altitude_msl=100,
                      uas_heading=90)

        # Bad longitude
        with self.assertRaises(ValueError):
            Telemetry(latitude=38,
                      longitude=-200,
                      altitude_msl=100,
                      uas_heading=90)

        # Bad heading
        with self.assertRaises(ValueError):
            Telemetry(latitude=38,
                      longitude=-76,
                      altitude_msl=100,
                      uas_heading=-90)

        # Bad type
        with self.assertRaises(ValueError):
            Telemetry(latitude=38,
                      longitude="Webster Field",
                      altitude_msl=100,
                      uas_heading=90)

    def test_serialize(self):
        """Test serialization"""
        t = Telemetry(latitude=38,
                      longitude=-76,
                      altitude_msl=100,
                      uas_heading=90)
        s = t.serialize()

        self.assertEqual(4, len(s))

        self.assertEqual(38, s['latitude'])
        self.assertEqual(-76, s['longitude'])
        self.assertEqual(100, s['altitude_msl'])
        self.assertEqual(90, s['uas_heading'])


class TestStationaryObstacle(unittest.TestCase):
    """Test the StationaryObstacle object. There is very little to see here."""

    def test_valid(self):
        """Test valid inputs"""
        # No exceptions
        StationaryObstacle(latitude=38,
                           longitude=-76,
                           cylinder_radius=100,
                           cylinder_height=200)

    def test_invalid(self):
        """Test invalid inputs"""
        # Bad latitude
        with self.assertRaises(ValueError):
            StationaryObstacle(latitude=120,
                               longitude=-76,
                               cylinder_radius=100,
                               cylinder_height=200)

        # Bad longitude
        with self.assertRaises(ValueError):
            StationaryObstacle(latitude=38,
                               longitude=-200,
                               cylinder_radius=100,
                               cylinder_height=200)

        # Bad radius
        with self.assertRaises(ValueError):
            StationaryObstacle(latitude=38,
                               longitude=-76,
                               cylinder_radius=-100,
                               cylinder_height=200)

        # Bad height
        with self.assertRaises(ValueError):
            StationaryObstacle(latitude=38,
                               longitude=-76,
                               cylinder_radius=100,
                               cylinder_height=-200)

        # Bad type
        with self.assertRaises(ValueError):
            StationaryObstacle(latitude=38,
                               longitude="Webster Field",
                               cylinder_radius=100,
                               cylinder_height=90)

    def test_serialize(self):
        """Test serialization"""
        o = StationaryObstacle(latitude=38,
                               longitude=-76,
                               cylinder_radius=100,
                               cylinder_height=200)
        s = o.serialize()

        self.assertEqual(4, len(s))

        self.assertEqual(38, s['latitude'])
        self.assertEqual(-76, s['longitude'])
        self.assertEqual(100, s['cylinder_radius'])
        self.assertEqual(200, s['cylinder_height'])


class TestMovingObstacle(unittest.TestCase):
    """Test the MovingObstacle object. There is very little to see here."""

    def test_valid(self):
        """Test valid inputs"""
        # No exceptions
        MovingObstacle(latitude=38,
                       longitude=-76,
                       altitude_msl=100,
                       sphere_radius=200)

    def test_invalid(self):
        """Test invalid inputs"""
        # Bad latitude
        with self.assertRaises(ValueError):
            MovingObstacle(latitude=120,
                           longitude=-76,
                           altitude_msl=100,
                           sphere_radius=200)

        # Bad longitude
        with self.assertRaises(ValueError):
            MovingObstacle(latitude=38,
                           longitude=-200,
                           altitude_msl=100,
                           sphere_radius=200)

        # Bad radius
        with self.assertRaises(ValueError):
            MovingObstacle(latitude=38,
                           longitude=-76,
                           altitude_msl=100,
                           sphere_radius=-200)

        # Bad type
        with self.assertRaises(ValueError):
            MovingObstacle(latitude=38,
                           longitude="Webster Field",
                           altitude_msl=100,
                           sphere_radius=90)

    def test_serialize(self):
        """Test serialization"""
        o = MovingObstacle(latitude=38,
                           longitude=-76,
                           altitude_msl=100,
                           sphere_radius=200)
        s = o.serialize()

        self.assertEqual(4, len(s))

        self.assertEqual(38, s['latitude'])
        self.assertEqual(-76, s['longitude'])
        self.assertEqual(100, s['altitude_msl'])
        self.assertEqual(200, s['sphere_radius'])
