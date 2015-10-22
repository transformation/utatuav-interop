"""Tests for the missions module."""

import datetime
import json
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import MissionConfig
from auvsi_suas.models import ServerInfo
from auvsi_suas.views.missions import active_mission
from auvsi_suas.views.missions import mission_for_request
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.test import TestCase
from django.utils import timezone

login_url = reverse('auvsi_suas:login')
missions_url = reverse('auvsi_suas:missions')


class TestMissionForRequest(TestCase):
    """Tests for function mission_for_request."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def create_config(self):
        """Creates a dummy config for testing."""
        pos = GpsPosition()
        pos.latitude = 10
        pos.longitude = 10
        pos.save()

        info = ServerInfo()
        info.timestamp = datetime.datetime.now()
        info.message = "Hello World"
        info.save()

        config = MissionConfig()
        config.is_active = False
        config.home_pos = pos
        config.emergent_last_known_pos = pos
        config.off_axis_target_pos = pos
        config.sric_pos = pos
        config.ir_primary_target_pos = pos
        config.ir_secondary_target_pos = pos
        config.air_drop_pos = pos
        config.server_info = info
        return config

    def test_noninteger_id(self):
        """Tests a non-integer mission ID in request."""
        params = {'mission': 'a'}
        _, err = mission_for_request(params)
        self.assertTrue(isinstance(err, HttpResponseBadRequest))

    def test_config_doesnt_exist(self):
        """Tests a mission ID for a mission that doesn't exist."""
        params = {'mission': '1'}
        _, err = mission_for_request(params)
        self.assertTrue(isinstance(err, HttpResponseBadRequest))

    def test_specified_mission(self):
        """Tests getting the mission for a specified ID."""
        config = self.create_config()
        config.is_active = False
        config.save()

        params = {'mission': str(config.pk)}
        recv_config, _ = mission_for_request(params)
        self.assertEqual(config, recv_config)

    def test_no_active_missions(self):
        """Tests when there are no active missions."""
        _, err = active_mission()
        self.assertTrue(isinstance(err, HttpResponseServerError))

        _, err = mission_for_request({})
        self.assertTrue(isinstance(err, HttpResponseServerError))

    def test_multiple_active_missions(self):
        """Tests when too many active missions."""
        config = self.create_config()
        config.is_active = True
        config.save()
        config = self.create_config()
        config.is_active = True
        config.save()

        _, err = active_mission()
        self.assertTrue(isinstance(err, HttpResponseServerError))

        _, err = mission_for_request({})
        self.assertTrue(isinstance(err, HttpResponseServerError))

    def test_active_mission(self):
        """Tests getting the single active mission."""
        config = self.create_config()
        config.is_active = True
        config.save()

        recv_config, _ = active_mission()
        self.assertEqual(config, recv_config)

        recv_config, _ = mission_for_request({})
        self.assertEqual(config, recv_config)


class TestMissionsViewLoggedOut(TestCase):
    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.get(missions_url)
        self.assertEqual(403, response.status_code)


class TestMissionsViewCommon(TestCase):
    """Common test setup"""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'superuser', 'email@example.com', 'superpass')
        self.superuser.save()

        # Login
        response = self.client.post(login_url, {
            'username': 'superuser',
            'password': 'superpass'
        })
        self.assertEqual(200, response.status_code)


class TestMissionsViewBasic(TestMissionsViewCommon):
    """Tests the missions view with minimal data."""

    def test_normal_user(self):
        """Normal users not allowed access."""
        user = User.objects.create_user('testuser', 'email@example.com',
                                        'testpass')
        user.save()

        # Login
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(200, response.status_code)

        response = self.client.get(missions_url)
        self.assertEqual(403, response.status_code)

    def test_post(self):
        """POST not allowed"""
        response = self.client.post(missions_url)
        self.assertEqual(405, response.status_code)

    def test_no_missions(self):
        """No missions results in empty list."""
        response = self.client.get(missions_url)
        self.assertEqual(200, response.status_code)

        self.assertEqual([], json.loads(response.content))


class TestMissionsViewSampleMission(TestMissionsViewCommon):
    """Tests the missions view with sample mission."""

    fixtures = ['testdata/sample_mission.json']

    def test_correct_json(self):
        """Response JSON is properly formatted."""
        response = self.client.get(missions_url)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(1, len(data))

        self.assertIn('id', data[0])
        self.assertEqual(3, data[0]['id'])

        self.assertIn('active', data[0])
        self.assertEqual(True, data[0]['active'])

        self.assertIn('home_pos', data[0])
        self.assertIn('latitude', data[0]['home_pos'])
        self.assertIn('longitude', data[0]['home_pos'])
        self.assertEqual(10.0, data[0]['home_pos']['latitude'])
        self.assertEqual(100.0, data[0]['home_pos']['longitude'])

        self.assertIn('mission_waypoints', data[0])
        for waypoint in data[0]['mission_waypoints']:
            self.assertIn('id', waypoint)
            self.assertIn('latitude', waypoint)
            self.assertIn('longitude', waypoint)
            self.assertIn('altitude_msl', waypoint)
            self.assertIn('order', waypoint)

        self.assertEqual(2, len(data[0]['mission_waypoints']))

        self.assertEqual(155, data[0]['mission_waypoints'][0]['id'])
        self.assertEqual(38.0, data[0]['mission_waypoints'][0]['latitude'])
        self.assertEqual(-76.0, data[0]['mission_waypoints'][0]['longitude'])
        self.assertEqual(30.0, data[0]['mission_waypoints'][0]['altitude_msl'])
        self.assertEqual(0, data[0]['mission_waypoints'][0]['order'])

        self.assertEqual(156, data[0]['mission_waypoints'][1]['id'])
        self.assertEqual(38.0, data[0]['mission_waypoints'][1]['latitude'])
        self.assertEqual(-76.0, data[0]['mission_waypoints'][1]['longitude'])
        self.assertEqual(60.0, data[0]['mission_waypoints'][1]['altitude_msl'])
        self.assertEqual(1, data[0]['mission_waypoints'][1]['order'])

        self.assertIn('search_grid_points', data[0])
        for point in data[0]['search_grid_points']:
            self.assertIn('id', point)
            self.assertIn('latitude', point)
            self.assertIn('longitude', point)
            self.assertIn('altitude_msl', point)
            self.assertIn('order', point)

        self.assertEqual(1, len(data[0]['search_grid_points']))

        self.assertEqual(150, data[0]['search_grid_points'][0]['id'])
        self.assertEqual(10.0, data[0]['search_grid_points'][0]['latitude'])
        self.assertEqual(100.0, data[0]['search_grid_points'][0]['longitude'])
        self.assertEqual(1000.0,
                         data[0]['search_grid_points'][0]['altitude_msl'])
        self.assertEqual(10, data[0]['search_grid_points'][0]['order'])

        self.assertIn('emergent_last_known_pos', data[0])
        self.assertIn('latitude', data[0]['emergent_last_known_pos'])
        self.assertIn('longitude', data[0]['emergent_last_known_pos'])
        self.assertEqual(10.0, data[0]['emergent_last_known_pos']['latitude'])
        self.assertEqual(100.0,
                         data[0]['emergent_last_known_pos']['longitude'])

        self.assertIn('off_axis_target_pos', data[0])
        self.assertIn('latitude', data[0]['off_axis_target_pos'])
        self.assertIn('longitude', data[0]['off_axis_target_pos'])
        self.assertEqual(10.0, data[0]['off_axis_target_pos']['latitude'])
        self.assertEqual(100.0, data[0]['off_axis_target_pos']['longitude'])

        self.assertIn('sric_pos', data[0])
        self.assertIn('latitude', data[0]['sric_pos'])
        self.assertIn('longitude', data[0]['sric_pos'])
        self.assertEqual(10.0, data[0]['sric_pos']['latitude'])
        self.assertEqual(100.0, data[0]['sric_pos']['longitude'])

        self.assertIn('ir_primary_target_pos', data[0])
        self.assertIn('latitude', data[0]['ir_primary_target_pos'])
        self.assertIn('longitude', data[0]['ir_primary_target_pos'])
        self.assertEqual(10.0, data[0]['ir_primary_target_pos']['latitude'])
        self.assertEqual(100.0, data[0]['ir_primary_target_pos']['longitude'])

        self.assertIn('ir_secondary_target_pos', data[0])
        self.assertIn('latitude', data[0]['ir_secondary_target_pos'])
        self.assertIn('longitude', data[0]['ir_secondary_target_pos'])
        self.assertEqual(10.0, data[0]['ir_secondary_target_pos']['latitude'])
        self.assertEqual(100.0,
                         data[0]['ir_secondary_target_pos']['longitude'])

        self.assertIn('air_drop_pos', data[0])
        self.assertIn('latitude', data[0]['air_drop_pos'])
        self.assertIn('longitude', data[0]['air_drop_pos'])
        self.assertEqual(10.0, data[0]['air_drop_pos']['latitude'])
        self.assertEqual(100.0, data[0]['air_drop_pos']['longitude'])
