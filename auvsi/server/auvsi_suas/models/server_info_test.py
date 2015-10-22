"""Tests for the server_info module."""

from server_info import ServerInfo
from django.test import TestCase
from django.utils import timezone


class TestServerInfoModel(TestCase):
    """Tests the ServerInfo model."""

    def test_unicode(self):
        """Tests the unicode method executes."""
        info = ServerInfo(timestamp=timezone.now(), team_msg='Test message.')
        info.save()

        info.__unicode__()

    def test_serialization(self):
        """Tests the JSON serialization method."""
        message = 'Hello, world.'
        time = timezone.now()

        info = ServerInfo(timestamp=time, team_msg=message)
        json_data = info.json()

        self.assertTrue('message' in json_data)
        self.assertEqual(json_data['message'], message)
        self.assertTrue('message_timestamp' in json_data)
        self.assertEqual(json_data['message_timestamp'], time.isoformat())
