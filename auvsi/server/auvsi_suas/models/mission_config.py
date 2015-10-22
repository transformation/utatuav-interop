"""Mission configuration model."""

import itertools
import logging
from auvsi_suas.patches.simplekml_patch import Color
from auvsi_suas.patches.simplekml_patch import AltitudeMode
from fly_zone import FlyZone
from gps_position import GpsPosition
from moving_obstacle import MovingObstacle
from obstacle_access_log import ObstacleAccessLog
from server_info import ServerInfo
from server_info_access_log import ServerInfoAccessLog
from stationary_obstacle import StationaryObstacle
from takeoff_or_landing_event import TakeoffOrLandingEvent
from time_period import TimePeriod
from uas_telemetry import UasTelemetry
from waypoint import Waypoint
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

# Logging for the module
logger = logging.getLogger(__name__)


class MissionConfig(models.Model):
    """The details for the active mission. There should only be one."""
    # Whether the mission is active. Only one mission can be active at a time.
    is_active = models.BooleanField(default=False)

    # The home position for use as a reference point. Should be the tents.
    home_pos = models.ForeignKey(GpsPosition,
                                 related_name="missionconfig_home_pos")

    # Valid areas for the UAS to fly.
    fly_zones = models.ManyToManyField(FlyZone)

    # The waypoints that define the mission waypoint path
    mission_waypoints = models.ManyToManyField(
        Waypoint,
        related_name='missionconfig_mission_waypoints')

    # The polygon that defines the search grid
    search_grid_points = models.ManyToManyField(
        Waypoint,
        related_name='missionconfig_search_grid_points')

    # The last known position of the emergent target
    emergent_last_known_pos = models.ForeignKey(
        GpsPosition,
        related_name='missionconfig_emergent_last_known_pos')

    # Off-axis target position
    off_axis_target_pos = models.ForeignKey(
        GpsPosition,
        related_name='missionconfig_off_axis_target_pos')

    # The SRIC position
    sric_pos = models.ForeignKey(GpsPosition,
                                 related_name='missionconfig_sric_pos')

    # The IR primary target position
    ir_primary_target_pos = models.ForeignKey(
        GpsPosition,
        related_name='missionconfig_ir_primary_target_pos')

    # The IR secondary target position
    ir_secondary_target_pos = models.ForeignKey(
        GpsPosition,
        related_name='missionconfig_ir_secondary_target_pos')

    # The air drop position
    air_drop_pos = models.ForeignKey(GpsPosition,
                                     related_name='missionconfig_air_drop_pos')

    # The server info
    server_info = models.ForeignKey(ServerInfo)

    # The stationary obstacles
    stationary_obstacles = models.ManyToManyField(StationaryObstacle)

    # The moving obstacles
    moving_obstacles = models.ManyToManyField(MovingObstacle)

    def __unicode__(self):
        """Descriptive text for use in displays."""
        mission_waypoints_str = ', '.join(
            ['%s' % wpt.__unicode__() for wpt in self.mission_waypoints.all()])
        search_grid_str = ', '.join(
            ['%s' % wpt.__unicode__()
             for wpt in self.search_grid_points.all()])
        stationary_obstacles_str = ', '.join(
            ['%s' % obst.__unicode__()
             for obst in self.stationary_obstacles.all()])
        moving_obstacles_str = ', '.join(
            ['%s' % obst.__unicode__()
             for obst in self.moving_obstacles.all()])

        return unicode(
            'MissionConfig (pk:%s, is_active: %s, home_pos:%s, '
            'mission_waypoints:[%s], search_grid:[%s], '
            'emergent_lkp:%s, off_axis:%s, '
            'sric_pos:%s, ir_primary_pos:%s, ir_secondary_pos:%s, '
            'air_drop_pos:%s, server_info:%s, stationary_obstacles:%s, '
            'moving_obstacles:%s)' %
            (str(self.pk), str(self.is_active), self.home_pos.__unicode__(),
             mission_waypoints_str, search_grid_str,
             self.emergent_last_known_pos.__unicode__(),
             self.off_axis_target_pos.__unicode__(),
             self.sric_pos.__unicode__(),
             self.ir_primary_target_pos.__unicode__(),
             self.ir_secondary_target_pos.__unicode__(),
             self.air_drop_pos.__unicode__(), self.server_info.__unicode__(),
             stationary_obstacles_str, moving_obstacles_str))

    def satisfied_waypoints(self, uas_telemetry_logs):
        """Determines whether the UAS satisfied the waypoints.

        Args:
            uas_telemetry_logs: A list of UAS Telemetry logs.
        Returns:
            A list of booleans where each value indicates whether the UAS
            satisfied the waypoint for that index.
        """
        waypoints_satisfied = []
        waypoints = self.mission_waypoints.order_by('order')
        for waypoint in waypoints:
            satisfied = False
            for uas_log in uas_telemetry_logs:
                distance = uas_log.uas_position.distance_to(waypoint.position)
                if distance < settings.SATISFIED_WAYPOINT_DIST_MAX_FT:
                    satisfied = True
                    break
            waypoints_satisfied.append(satisfied)
        return waypoints_satisfied

    def evaluate_teams(self):
        """Evaluates the teams (non admin users) of the competition.

        Returns:
            A map from user to evaluate data. The evaluation data has the
            following map structure:
            {
                'waypoints_satisfied': {
                    id: Boolean,
                }
                'out_of_bounds_time': Seconds spent out of bounds,
                'interop_times': {
                    'server_info': {'max': Value, 'avg': Value},
                    'obst_info': {'max': Value, 'avg': Value},
                    'uas_telem': {'max': Value, 'avg': Value},
                },
                'stationary_obst_collision': {
                    id: Boolean
                },
                'moving_obst_collision': {
                    id: Boolean
                }
            }
        """
        # Start a results map from user to evaluation data
        results = {}

        # Fill in evaluation data for each user except admins
        users = User.objects.all()
        logger.info('Starting team evaluations.')

        for user in users:
            # Ignore admins.
            if user.is_superuser:
                continue

            logger.info('Evaluation starting for user: %s.' % user.username)

            # Start the evaluation data structure.
            eval_data = results.setdefault(user, {})

            # Find the user's flights.
            flight_periods = TakeoffOrLandingEvent.flights(user)
            uas_period_logs = UasTelemetry.dedupe(
                UasTelemetry.by_time_period(user, flight_periods))
            uas_logs = list(itertools.chain.from_iterable(uas_period_logs))

            # Determine if the uas hit the waypoints.
            waypoints_hit = self.satisfied_waypoints(uas_logs)
            waypoints_keyed = {}
            for i, hit in enumerate(waypoints_hit):
                waypoints_keyed[i + 1] = hit
            eval_data['waypoints_satisfied'] = waypoints_keyed

            # Determine if the uas went out of bounds. This must be done for
            # each period individually so time between periods isn't counted as
            # out of bounds time. Note that this calculates reported time out
            # of bounds, not actual or possible time spent out of bounds.
            out_of_bounds_time = 0
            for logs in uas_period_logs:
                out_of_bounds_time += FlyZone.out_of_bounds(
                    self.fly_zones.all(), logs)
            eval_data['out_of_bounds_time'] = out_of_bounds_time

            # Determine interop rates.
            interop_times = eval_data.setdefault('interop_times', {})

            server_info_times = ServerInfoAccessLog.rates(user, flight_periods)
            obstacle_times = ObstacleAccessLog.rates(user, flight_periods)
            uas_telemetry_times = UasTelemetry.rates(
                user, flight_periods,
                time_period_logs=uas_period_logs)

            interop_times['server_info'] = {
                'max': server_info_times[0],
                'avg': server_info_times[1]
            }
            interop_times['obst_info'] = {
                'max': obstacle_times[0],
                'avg': obstacle_times[1]
            }
            interop_times['uas_telem'] = {
                'max': uas_telemetry_times[0],
                'avg': uas_telemetry_times[1]
            }

            # Determine collisions with stationary and moving obstacles.
            stationary_collisions = eval_data.setdefault(
                'stationary_obst_collision', {})
            for obst in self.stationary_obstacles.all():
                collision = obst.evaluate_collision_with_uas(uas_logs)
                stationary_collisions[obst.pk] = collision

            moving_collisions = eval_data.setdefault(
                'moving_obst_collision', {})
            for obst in self.moving_obstacles.all():
                collision = obst.evaluate_collision_with_uas(uas_logs)
                moving_collisions[obst.pk] = collision

        return results

    def json(self):
        """Return a dict, for conversion to JSON."""
        ret = {
            'id': self.pk,
            'active': self.is_active,
            'home_pos': {
                'latitude': self.home_pos.latitude,
                'longitude': self.home_pos.longitude,
            },
            "fly_zones": [],  # Filled in below
            "mission_waypoints": [],  # Filled in below
            "search_grid_points": [],  # Filled in below
            "emergent_last_known_pos": {
                "latitude": self.emergent_last_known_pos.latitude,
                "longitude": self.emergent_last_known_pos.longitude,
            },
            'off_axis_target_pos': {
                'latitude': self.off_axis_target_pos.latitude,
                'longitude': self.off_axis_target_pos.longitude,
            },
            'sric_pos': {
                'latitude': self.sric_pos.latitude,
                'longitude': self.sric_pos.longitude,
            },
            'ir_primary_target_pos': {
                'latitude': self.ir_primary_target_pos.latitude,
                'longitude': self.ir_primary_target_pos.longitude,
            },
            'ir_secondary_target_pos': {
                'latitude': self.ir_secondary_target_pos.latitude,
                'longitude': self.ir_secondary_target_pos.longitude,
            },
            'air_drop_pos': {
                'latitude': self.air_drop_pos.latitude,
                'longitude': self.air_drop_pos.longitude,
            },
            'stationary_obstacles': [],  # Filled in below
            'moving_obstacles': [],  # Filled in below
        }
        for zone in self.fly_zones.all():
            pts = [
                {
                    "latitude": bpt.position.gps_position.latitude,
                    "longitude": bpt.position.gps_position.longitude,
                    "order": bpt.order
                } for bpt in zone.boundary_pts.order_by('order')
            ]
            ret['fly_zones'].append({
                "boundary_pts": pts,
                "altitude_msl_min": zone.altitude_msl_min,
                "altitude_msl_max": zone.altitude_msl_max
            })
        for waypoint in self.mission_waypoints.all():
            ret['mission_waypoints'].append({
                'id': waypoint.pk,
                'latitude': waypoint.position.gps_position.latitude,
                'longitude': waypoint.position.gps_position.longitude,
                'altitude_msl': waypoint.position.altitude_msl,
                'order': waypoint.order,
            })

        for point in self.search_grid_points.all():
            ret['search_grid_points'].append({
                'id': point.pk,
                'latitude': point.position.gps_position.latitude,
                'longitude': point.position.gps_position.longitude,
                'altitude_msl': point.position.altitude_msl,
                'order': point.order,
            })
        for obst in self.stationary_obstacles.all():
            ret['stationary_obstacles'].append({
                'id': obst.pk,
                'latitude': obst.gps_position.latitude,
                'longitude': obst.gps_position.longitude,
                'cylinder_radius': obst.cylinder_radius,
                'cylinder_height': obst.cylinder_height,
            })
        for obst in self.moving_obstacles.all():
            ret['moving_obstacles'].append({
                'id': obst.pk,
                'speed_avg': obst.speed_avg,
                'sphere_radius': obst.sphere_radius,
            })
        return ret

    @classmethod
    def kml_all(cls, kml, missions=None):
        """
        Appends kml nodes describing all mission configurations.

        Args:
            kml: A simpleKML Container to which the mission data will be added
            missions: Optional list of mission for which to generate KML. If
                None, it will use all missions.
        """
        if not missions:
            missions = MissionConfig.objects.all()

        for mission in missions:
            mission.kml(kml)

    def kml(self, kml):
        """
        Appends kml nodes describing this mission configurations.

        Args:
            kml: A simpleKML Container to which the mission data will be added
        """
        mission_name = 'Mission {}'.format(self.pk)
        kml_folder = kml.newfolder(name=mission_name)

        # Static Points
        locations = {
            'Home Position': self.home_pos,
            'Emergent LKP': self.emergent_last_known_pos,
            'Off Axis': self.off_axis_target_pos,
            'SRIC': self.sric_pos,
            'IR Primary': self.ir_primary_target_pos,
            'IR Secondary': self.ir_secondary_target_pos,
            'Air Drop': self.air_drop_pos,
        }
        for key, point in locations.iteritems():
            gps = (point.longitude, point.latitude)
            wp = kml_folder.newpoint(name=key, coords=[gps])
            wp.description = str(point)

        # Waypoints
        waypoints_folder = kml_folder.newfolder(name='Waypoints')
        linestring = waypoints_folder.newlinestring(name='Waypoints')
        waypoints = []
        waypoint_num = 1
        for waypoint in self.mission_waypoints.all():
            gps = waypoint.position.gps_position
            coord = (gps.longitude, gps.latitude,
                     waypoint.position.altitude_msl)
            waypoints.append(coord)

            # Add waypoint marker
            wp = waypoints_folder.newpoint(name=str(waypoint_num),
                                           coords=[coord])
            wp.description = str(waypoint)
            wp.altitudemode = AltitudeMode.absolute
            wp.extrude = 1
            wp.visibility = False
            waypoint_num += 1
        linestring.coords = waypoints

        # Waypoints Style
        linestring.altitudemode = AltitudeMode.absolute
        linestring.extrude = 1
        linestring.style.linestyle.color = Color.black
        linestring.style.polystyle.color = Color.changealphaint(100,
                                                                Color.green)

        # Search Area
        search_area_folder = kml_folder.newfolder(name='Search Area')
        search_area = []
        search_area_num = 1
        for point in self.search_grid_points.all():
            gps = point.position.gps_position
            coord = (gps.longitude, gps.latitude, point.position.altitude_msl)
            search_area.append(coord)

            # Add boundary marker
            wp = search_area_folder.newpoint(name=str(search_area_num),
                                             coords=[coord])
            wp.description = str(point)
            wp.visibility = False
            search_area_num += 1
        if search_area:
            # Create search area polygon.
            pol = search_area_folder.newpolygon(name='Search Area')
            search_area.append(search_area[0])
            pol.outerboundaryis = search_area
            # Search Area Style.
            pol.style.linestyle.color = Color.black
            pol.style.linestyle.width = 2
            pol.style.polystyle.color = Color.changealphaint(50, Color.blue)

        # Stationary Obstacles
        stationary_obstacles_folder = kml_folder.newfolder(
            name='Stationary Obstacles')
