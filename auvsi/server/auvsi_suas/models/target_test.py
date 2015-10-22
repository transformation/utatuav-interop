"""Tests for the target module."""

import os.path
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import Target
from auvsi_suas.models import TargetType
from auvsi_suas.models import Color
from auvsi_suas.models import Shape
from auvsi_suas.models import Orientation
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone


class TestTarget(TestCase):
    """Tests for the Target model."""

    def setUp(self):
        """Sets up the tests."""
        self.user = User.objects.create_user('user', 'email@example.com',
                                             'pass')

    def test_valid(self):
        """Test creating a valid target."""
        with open(os.path.join(settings.BASE_DIR,
                               'auvsi_suas/fixtures/testdata/S.jpg')) as f:
            thumb = SimpleUploadedFile('thumb.jpg', f.read())

        l = GpsPosition(latitude=38, longitude=-76)
        l.save()

        t = Target(
            user=self.user,
            target_type=TargetType.standard,
            location=l,
            orientation=Orientation.s,
            shape=Shape.square,
            background_color=Color.white,
            alphanumeric='ABC',
            alphanumeric_color=Color.black,
            description='Test target',
            thumbnail=thumb)
        t.save()

    def test_unicode(self):
        """Test unicode conversion."""
        with open(os.path.join(settings.BASE_DIR,
                               'auvsi_suas/fixtures/testdata/S.jpg')) as f:
            thumb = SimpleUploadedFile('thumb.jpg', f.read())

        l = GpsPosition(latitude=38, longitude=-76)
        l.save()

        t = Target(
            user=self.user,
            target_type=TargetType.standard,
            location=l,
            orientation=Orientation.s,
            shape=Shape.square,
            background_color=Color.white,
            alphanumeric='ABC',
            alphanumeric_color=Color.black,
            description='Test target',
            thumbnail=thumb)
        t.save()

        self.assertTrue(t.__unicode__())

    def test_minimal_unicode(self):
        """Unicode with only user and target."""
        t = Target(user=self.user, target_type=TargetType.standard)
        t.save()

        self.assertTrue(t.__unicode__())

    def test_null_fields(self):
        """Only user and target type."""
        t = Target(user=self.user, target_type=TargetType.standard)
        t.save()

    def test_json(self):
        """Test target JSON."""
        l = GpsPosition(latitude=38, longitude=-76)
        l.save()

        t = Target(
            user=self.user,
            target_type=TargetType.standard,
            location=l,
            orientation=Orientation.s,
            shape=Shape.square,
            background_color=Color.white,
            alphanumeric='ABC',
            alphanumeric_color=Color.black,
            description='Test target')
        t.save()

        d = t.json()

        self.assertIn('id', d)
        self.assertEqual(self.user.pk, d['user'])
        self.assertEqual('standard', d['type'])
        self.assertEqual(38, d['latitude'])
        self.assertEqual(-76, d['longitude'])
        self.assertEqual('s', d['orientation'])
        self.assertEqual('square', d['shape'])
        self.assertEqual('white', d['background_color'])
        self.assertEqual('ABC', d['alphanumeric'])
        self.assertEqual('black', d['alphanumeric_color'])
        self.assertEqual('Test target', d['description'])

    def test_minimal_json(self):
        """Test target JSON with minimal data."""
        t = Target(user=self.user, target_type=TargetType.standard)
        t.save()

        d = t.json()

        self.assertIn('id', d)
        self.assertEqual(self.user.pk, d['user'])
        self.assertEqual('standard', d['type'])
        self.assertEqual(None, d['latitude'])
        self.assertEqual(None, d['longitude'])
        self.assertEqual(None, d['orientation'])
        self.assertEqual(None, d['shape'])
        self.assertEqual(None, d['background_color'])
        self.assertEqual(None, d['alphanumeric'])
        self.assertEqual(None, d['alphanumeric_color'])
        self.assertEqual(None, d['description'])
