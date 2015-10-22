"""Tests for the teams module."""

import functools
import json
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.models import UasTelemetry
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

login_url = reverse('auvsi_suas:login')
teams_url = reverse('auvsi_suas:teams')
teams_id_url = functools.partial(reverse, 'auvsi_suas:teams_id')


class TestTeamsViewLoggedOut(TestCase):
    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.get(teams_url)
        self.assertEqual(403, response.status_code)


class TestTeamsView(TestCase):
    """Tests the teams view."""

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

    def create_data(self):
        """Create a basic sample dataset."""
        self.user1 = User.objects.create_user('user1', 'email@example.com',
                                              'testpass')
        self.user1.save()

        self.user2 = User.objects.create_user('user2', 'email@example.com',
                                              'testpass')
        self.user2.save()

        # user1 is flying
        event = TakeoffOrLandingEvent(user=self.user1, uas_in_air=True)
        event.save()

        # user2 has landed
        event = TakeoffOrLandingEvent(user=self.user2, uas_in_air=True)
        event.save()
        event = TakeoffOrLandingEvent(user=self.user2, uas_in_air=False)
        event.save()

        # user2 is active
        self.timestamp = timezone.now()

        gps = GpsPosition(latitude=38.6462, longitude=-76.2452)
        gps.save()

        pos = AerialPosition(gps_position=gps, altitude_msl=0)
        pos.save()

        telem = UasTelemetry(user=self.user2, uas_position=pos, uas_heading=90)
        telem.save()
        telem.timestamp = self.timestamp
        telem.save()

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

        response = self.client.get(teams_url)
        self.assertEqual(403, response.status_code)

    def test_no_users(self):
        """No users results in empty list, no superusers."""
        response = self.client.get(teams_url)
        self.assertEqual(200, response.status_code)

        self.assertEqual([], json.loads(response.content))

    def test_post(self):
        """POST not allowed"""
        response = self.client.post(teams_url)
        self.assertEqual(405, response.status_code)

    def test_correct_json(self):
        """Response JSON is properly formatted."""
        self.create_data()

        response = self.client.get(teams_url)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(2, len(data))

        for user in data:
            self.assertIn('id', user)
            self.assertIn('name', user)
            self.assertIn('in_air', user)
            self.assertIn('active', user)

    def test_users_correct(self):
        """User names and status correct."""
        self.create_data()

        response = self.client.get(teams_url)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        names = [d['name'] for d in data]
        self.assertIn('user1', names)
        self.assertIn('user2', names)

        user1 = data[names.index('user1')]
        self.assertEqual(True, user1['in_air'])
        self.assertEqual(False, user1['active'])

        user2 = data[names.index('user2')]
        self.assertEqual(False, user2['in_air'])
        self.assertEqual(True, user2['active'])


class TestTeamsIdViewLoggedOut(TestCase):
    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.get(teams_id_url(args=[1]))
        self.assertEqual(403, response.status_code)


class TestTeamsIdView(TestCase):
    """Tests the teams-by-id view."""

    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'email@example.com',
                                              'testpass')
        self.user1.save()

        self.superuser = User.objects.create_superuser(
            'superuser', 'email@example.com', 'superpass')
        self.superuser.save()

        # Login
        response = self.client.post(login_url, {
            'username': 'superuser',
            'password': 'superpass'
        })
        self.assertEqual(200, response.status_code)

    def test_bad_id(self):
        """Invalid user id rejected"""
        response = self.client.get(teams_id_url(args=[999]))
        self.assertGreaterEqual(400, response.status_code)

    def test_correct_user(self):
        """User requested is correct"""
        response = self.client.get(teams_id_url(args=[self.user1.pk]))
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual('user1', data['name'])
        self.assertEqual(self.user1.pk, data['id'])
        self.assertEqual(False, data['in_air'])
        self.assertEqual(False, data['active'])

    def test_bad_json(self):
        """Invalid json rejected"""
        response = self.client.put(teams_id_url(args=[self.user1.pk]),
                                   'Hi there!')
        self.assertGreaterEqual(400, response.status_code)

    def test_invalid_in_air(self):
        """invalid in_air rejected"""
        data = json.dumps({
            'name': self.user1.username,
            'id': self.user1.pk,
            'active': False,
            'in_air': 'Hi!',
        })

        response = self.client.put(teams_id_url(args=[self.user1.pk]), data)
        self.assertGreaterEqual(400, response.status_code)

    def test_no_extra_events(self):
        """No new TakeoffOrLandingEvents created if status doesn't change"""
        data = json.dumps({
            'name': self.user1.username,
            'id': self.user1.pk,
            'active': False,
            'in_air': False,
        })

        response = self.client.put(teams_id_url(args=[self.user1.pk]), data)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(0, TakeoffOrLandingEvent.objects.count())

    def test_update_in_air(self):
        """In-air can be updated"""
        data = json.dumps({
            'name': self.user1.username,
            'id': self.user1.pk,
            'active': False,
            'in_air': True,
        })

        response = self.client.put(teams_id_url(args=[self.user1.pk]), data)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(True, data['in_air'])

        # Event created
        event = TakeoffOrLandingEvent.objects.get()
        self.assertEqual(self.user1, event.user)
        self.assertEqual(True, event.uas_in_air)

    def test_name_ignored(self):
        """name field ignored"""
        expected = self.user1.username

        data = json.dumps({
            'name': 'Hello World!',
            'id': self.user1.pk,
            'active': False,
            'in_air': False,
        })

        response = self.client.put(teams_id_url(args=[self.user1.pk]), data)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(expected, data['name'])

    def test_id_ignored(self):
        """id field ignored"""
        expected = self.user1.pk

        data = json.dumps({
            'name': self.user1.username,
            'id': 999,
            'active': False,
            'in_air': False,
        })

        response = self.client.put(teams_id_url(args=[self.user1.pk]), data)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(expected, data['id'])

    def test_active_ignored(self):
        """active field ignored"""
        data = json.dumps({
            'name': self.user1.username,
            'id': self.user1.pk,
            'active': True,
            'in_air': False,
        })

        response = self.client.put(teams_id_url(args=[self.user1.pk]), data)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(False, data['active'])
