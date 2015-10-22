"""Tests for the server_info module."""

import time
import json
import logging
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import MissionConfig
from auvsi_suas.models import ServerInfo
from auvsi_suas.models import ServerInfoAccessLog
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase

login_url = reverse('auvsi_suas:login')
info_url = reverse('auvsi_suas:server_info')


class TestServerInfoLoggedOut(TestCase):
    """Tests the ServerInfo view logged out."""

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.get(info_url)
        self.assertEqual(403, response.status_code)


class TestServerInfoView(TestCase):
    """Tests the server_info view."""

    def setUp(self):
        """Sets up the client, server info URL, and user."""
        cache.clear()
        self.user = User.objects.create_user('testuser', 'testemail@x.com',
                                             'testpass')
        self.user.save()

        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass',
        })
        self.assertEqual(200, response.status_code)

        self.info = ServerInfo()
        self.info.team_msg = 'test message'
        self.info.save()

        gpos = GpsPosition(latitude=0, longitude=0)
        gpos.save()

        self.mission = MissionConfig()
        self.mission.is_active = True
        self.mission.home_pos = gpos
        self.mission.emergent_last_known_pos = gpos
        self.mission.off_axis_target_pos = gpos
        self.mission.sric_pos = gpos
        self.mission.ir_primary_target_pos = gpos
        self.mission.ir_secondary_target_pos = gpos
        self.mission.air_drop_pos = gpos
        self.mission.server_info = self.info
        self.mission.save()

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        response = self.client.post(info_url)
        self.assertEqual(405, response.status_code)

    def test_no_active_mission(self):
        """Tests that no active mission returns 500."""
        self.mission.is_active = False
        self.mission.save()

        response = self.client.get(info_url)
        self.assertEqual(500, response.status_code)

    def test_correct_log_and_response(self):
        """Tests that access is logged and returns valid response."""
        response = self.client.get(info_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(ServerInfoAccessLog.objects.all()), 1)

        access_log = ServerInfoAccessLog.objects.all()[0]
        self.assertEqual(access_log.user, self.user)

        json_data = json.loads(response.content)
        self.assertTrue('message' in json_data)
        self.assertTrue('message_timestamp' in json_data)
        self.assertTrue('server_time' in json_data)

    def test_loadtest(self):
        """Tests the max load the view can handle."""
        if not settings.TEST_ENABLE_LOADTEST:
            return

        total_ops = 0
        start_t = time.clock()
        while time.clock() - start_t < settings.TEST_LOADTEST_TIME:
            self.client.get(info_url)
            total_ops += 1
        end_t = time.clock()
        total_t = end_t - start_t
        op_rate = total_ops / total_t

        print 'Server Info Rate (%f)' % op_rate
        self.assertGreaterEqual(
            op_rate, settings.TEST_LOADTEST_INTEROP_MIN_RATE)
