"""Tests for the evaluate_teams module."""

import logging
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


class TestEvaluateTeams(TestCase):
    """Tests the evaluate_teams view."""

    fixtures = ['testdata/sample_mission.json']

    def setUp(self):
        """Sets up the tests."""
        # Create nonadmin user
        self.nonadmin_user = User.objects.create_user(
            'testuser', 'testemail@x.com', 'testpass')
        self.nonadmin_user.save()
        self.nonadmin_client = Client()
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            'testuser2', 'testemail@x.com', 'testpass')
        self.admin_user.save()
        self.admin_client = Client()
        # Create URLs for testing
        self.login_url = reverse('auvsi_suas:login')
        self.eval_url = reverse('auvsi_suas:evaluate_teams')

    def test_evaluate_teams_nonadmin(self):
        """Tests that you can only access data as admin."""
        client = self.client
        login_url = self.login_url
        eval_url = self.eval_url
        client.post(login_url,
                    {'username': 'testuser',
                     'password': 'testpass'})
        response = client.get(eval_url)
        self.assertEqual(403, response.status_code)

    def test_invalid_mission(self):
        """Tests that an invalid mission ID results in error."""
        client = self.client
        login_url = self.login_url
        eval_url = self.eval_url
        client.post(login_url,
                    {'username': 'testuser',
                     'password': 'testpass'})

        response = client.get(eval_url, {'mission': 100000})
        self.assertGreaterEqual(response.status_code, 400)

    def test_evaluate_teams(self):
        """Tests the CSV method."""
        client = self.client
        login_url = self.login_url
        eval_url = self.eval_url
        client.post(login_url,
                    {'username': 'testuser2',
                     'password': 'testpass'})
        response = client.get(eval_url)
        self.assertEqual(response.status_code, 200)
        csv_data = response.content
        # Check correct number of rows
        self.assertEqual(len(csv_data.split('\n')), 5)
        # Check some headers
        self.assertTrue('username' in csv_data)
        self.assertTrue('interop_times.server_info.max' in csv_data)
        # Check username fields
        self.assertTrue('user0' in csv_data)
        self.assertTrue('user1' in csv_data)
