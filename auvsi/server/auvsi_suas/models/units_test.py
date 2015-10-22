"""Tests for the units module."""

from auvsi_suas.models import units
from django.test import TestCase


class TestKilometersToFeet(TestCase):
    """Tests the conversion from kilometers to feet."""

    def test_km_to_ft(self):
        """Performs a data-driven test of the conversion."""
        threshold = 5  # ft

        cases = [
            # (km, ft_actual)
            (0,    0),
            (1,    3280.84),
            (1.5,  4921.26),
            (100,  328084),
        ]  # yapf: disable

        for (km, ft_actual) in cases:
            self.assertLess(abs(units.kilometers_to_feet(km) - ft_actual),
                            threshold)


class TestKnotsToFeetPerSecond(TestCase):
    """Tests the conversion from knots to feet per second."""

    def test_knots_to_fps(self):
        """Performs a data-drive test of the conversion."""
        threshold = 5  # ft/s

        cases = [
            # (knots, fps)
            (0.1,     0.168781),
            (1,       1.68781),
            (10,      16.8781),
            (100,     168.781),
        ]  # yapf: disable

        for (knots, fps_actual) in cases:
            self.assertLess(
                abs(units.knots_to_feet_per_second(knots) - fps_actual),
                threshold)
