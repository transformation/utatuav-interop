"""Implementation of data generation for interoperability.

This is team specific and the code here represents a simulation.
"""

import abc
import logging


class DataGenerator(object):
    """Base class for a data generator which creates UAS telemetry."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_uas_telemetry(self, cur_time):
        """Gets the UAS telemetry position at the given time.

        Args:
            cur_time: The time to get UAS telemetry at.
        Returns:
            A tuple (latitude, longitude, altitude_msl, uas_heading) where
            the values are in degrees, degrees, feet, degrees respectively.
        """
        logging.Fatal('Unimplemented.')


class ZeroValueGenerator(DataGenerator):
    """Generates zero values for all of time."""

    def get_uas_telemetry(self, cur_time):
        """Overrides base method."""
        return (0, 0, 0, 0)
