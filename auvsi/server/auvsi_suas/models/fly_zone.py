"""Fly zone model."""
from auvsi_suas.patches.simplekml_patch import AltitudeMode
from auvsi_suas.patches.simplekml_patch import Color
import numpy as np
from django.db import models
from matplotlib import path as mplpath
from waypoint import Waypoint


class FlyZone(models.Model):
    """An approved area for UAS flight. UAS shall be in at least one zone."""
    # The polygon defining the boundary of the zone.
    boundary_pts = models.ManyToManyField(Waypoint)
    # The minimum altitude of the zone (MSL) in feet
    altitude_msl_min = models.FloatField()
    # The maximum altitude of the zone (MSL) in feet
    altitude_msl_max = models.FloatField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        boundary_strs = ["%s" % wpt.__unicode__()
                         for wpt in self.boundary_pts.all()]
        boundary_str = ", ".join(boundary_strs)
        return unicode("FlyZone (pk:%s, alt_min:%s, alt_max:%s, "
                       "boundary_pts:[%s])" %
                       (str(self.pk), str(self.altitude_msl_min),
                        str(self.altitude_msl_max), boundary_str))

    def contains_pos(self, aerial_pos):
        """Whether the given pos is inside the zone.

        Args:
            aerial_pos: The AerialPosition to test.
        Returns:
            Whether the given position is inside the flight boundary.
        """
        return self.contains_many_pos([aerial_pos])[0]

    def contains_many_pos(self, aerial_pos_list):
        """Evaluates a list of positions more efficiently than inidividually.

        Args:
            aerial_pos_list: A list of AerialPositions to test.
        Returns:
            A list storing whether each position is inside the boundary.
        """
        # Get boundary points
        ordered_pts = self.boundary_pts.order_by('order')
        path_pts = [[wpt.position.gps_position.latitude,
                     wpt.position.gps_position.longitude]
                    for wpt in ordered_pts]
        # First check enough points to define a polygon
        if len(path_pts) < 3:
            return [False] * len(aerial_pos_list)

        # Create path to use for testing polygon inclusion
        path_pts.append(path_pts[0])
        path = mplpath.Path(np.array(path_pts))

        # Test each aerial position for altitude
        results = []
        for aerial_pos in aerial_pos_list:
            # Check altitude bounds
            alt = aerial_pos.altitude_msl
            altitude_check = (
                alt <= self.altitude_msl_max and alt >= self.altitude_msl_min
            )
            results.append(altitude_check)

        # Create a list of positions to test whether inside polygon
        polygon_test_point_ids = [cur_id
                                  for cur_id in range(len(aerial_pos_list))
                                  if results[cur_id]]
        if len(polygon_test_point_ids) == 0:
            return results
        polygon_test_points = [[aerial_pos_list[cur_id].gps_position.latitude,
                                aerial_pos_list[cur_id].gps_position.longitude]
                               for cur_id in polygon_test_point_ids]

        # Test each point for inside polygon
        polygon_test_results = path.contains_points(
            np.array(polygon_test_points))
        for test_id in range(len(polygon_test_point_ids)):
            cur_id = polygon_test_point_ids[test_id]
            results[cur_id] = (polygon_test_results[test_id] == True)

        return results

    @classmethod
    def out_of_bounds(cls, fly_zones, uas_telemetry_logs):
        """Determines amount of time spent out of bounds.

        Args:
            fly_zones: The list of FlyZone that the UAS must be in.
            uas_telemetry_logs: A list of UasTelemetry logs sorted by timestamp
                which demonstrate the flight of the UAS.
        Returns:
            The floating point total time in seconds spent out of bounds as
            indicated by the telemetry logs.
        """
        # Get the aerial positions for the logs
        aerial_pos_list = [cur_log.uas_position
                           for cur_log in uas_telemetry_logs]
        log_ids_to_process = range(len(aerial_pos_list))

        # Evaluate zones against the logs, eliminating satisfied ones, until
        # only the out of boundary ids remain
        for zone in fly_zones:
            # Stop processing if no ids
            if len(log_ids_to_process) == 0:
                break
            # Evaluate the positions still not satisfied
            cur_positions = [aerial_pos_list[cur_id]
                             for cur_id in log_ids_to_process]
            satisfied_positions = zone.contains_many_pos(cur_positions)
            # Retain those which were not satisfied in this pass
            log_ids_to_process = [log_ids_to_process[cur_id]
                                  for cur_id in range(len(log_ids_to_process))
                                  if not satisfied_positions[cur_id]]

        # Positions that remain are out of bound positions, compute total time
        total_time = 0
        for cur_id in log_ids_to_process:
            # Ignore first ID position as no start time for comparison
            if cur_id == 0:
                continue
            # Track time between previous and current out of bounds. This is a
            # simplification of time spent out of bounds.
            cur_log = uas_telemetry_logs[cur_id]
            prev_log = uas_telemetry_logs[cur_id - 1]
            time_diff = (cur_log.timestamp - prev_log.timestamp
                         ).total_seconds()
            total_time += time_diff

        return total_time

    @classmethod
    def kml_all(cls, kml):
        """
        Appends kml nodes describing all flyzone.

        Args:
            kml: A simpleKML Container to which the fly zones will be added
        """
        for flyzone in FlyZone.objects.all():
            flyzone.kml(kml)

    def kml(self, kml):
        """
        Appends kml nodes describing this flyzone.

        Args:
            kml: A simpleKML Container to which the fly zone will be added
        """

        zone_name = 'Fly Zone {}'.format(self.pk)
        pol = kml.newpolygon(name=zone_name)
        fly_zone = []
        flyzone_num = 1
        for point in self.boundary_pts.all():
            gps = point.position.gps_position
            coord = (gps.longitude, gps.latitude, point.position.altitude_msl)
            fly_zone.append(coord)

            # Add boundary marker
            wp = kml.newpoint(name=str(flyzone_num), coords=[coord])
            wp.description = str(point)
            wp.visibility = False
            flyzone_num += 1
        fly_zone.append(fly_zone[0])
        pol.outerboundaryis = fly_zone

        # Search Area Style
        pol.style.linestyle.color = Color.red
        pol.style.linestyle.width = 3
        pol.style.polystyle.color = Color.changealphaint(50, Color.green)
