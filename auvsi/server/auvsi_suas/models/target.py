"""Target model."""

import enum
from gps_position import GpsPosition
from django.conf import settings
from django.db import models


class Choices(enum.IntEnum):
    """Base class for enums used to limit Django field choices,
    plus other helper methods.

    Item names should be lowercase to work properly with lookup().
    """

    @classmethod
    def choices(cls):
        """Provide choices for Django's IntField.choices.

        Returns:
            Enum values in an iterator to be passed to IntField.choices.
            The enum value is used as the field key, and the name as the
            description.
        """
        return [(int(v), k) for k, v in cls.__members__.items()]

    @classmethod
    def lookup(cls, s):
        """Lookup value from name.

        Args:
            s: name to lookup; case insensitive

        Returns:
            Value associated with name

        Raises:
            KeyError: name not valid
        """
        return cls.__members__[str(s).lower()]

    @classmethod
    def names(cls):
        """Names of choices

        Returns:
            List of names of values
        """
        return cls.__members__.keys()


@enum.unique
class TargetType(Choices):
    """Valid target types.

    Warning: DO NOT change/reuse values, or compatibility will be lost with
    old data sets. Only add new values to the end.
    """
    standard = 1
    qrc = 2
    off_axis = 3
    emergent = 4
    ir = 5


@enum.unique
class Orientation(Choices):
    """Valid target orientations.

    Warning: DO NOT change/reuse values, or compatibility will be lost with
    old data sets. Only add new values to the end.
    """
    n = 1
    ne = 2
    e = 3
    se = 4
    s = 5
    sw = 6
    w = 7
    nw = 8


@enum.unique
class Shape(Choices):
    """Valid target shapes.

    Warning: DO NOT change/reuse values, or compatibility will be lost with
    old data sets. Only add new values to the end.
    """
    circle = 1
    semicircle = 2
    quarter_circle = 3
    triangle = 4
    square = 5
    rectangle = 6
    trapezoid = 7
    pentagon = 8
    hexagon = 9
    heptagon = 10
    octagon = 11
    star = 12
    cross = 13


@enum.unique
class Color(Choices):
    """Valid target colors.

    Warning: DO NOT change/reuse values, or compatibility will be lost with
    old data sets. Only add new values to the end.
    """
    white = 1
    black = 2
    gray = 3
    red = 4
    blue = 5
    green = 6
    yellow = 7
    purple = 8
    brown = 9
    orange = 10


class Target(models.Model):
    """Target represents a single target submission for a team."""
    # The user which submitted and owns this target.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)

    # Target type.
    target_type = models.IntegerField(choices=TargetType.choices())

    # Target location.
    location = models.ForeignKey(GpsPosition, null=True, blank=True)

    # Target orientation.
    orientation = models.IntegerField(choices=Orientation.choices(),
                                      null=True,
                                      blank=True)

    # Target shape.
    shape = models.IntegerField(choices=Shape.choices(), null=True, blank=True)

    # Target background color.
    background_color = models.IntegerField(choices=Color.choices(),
                                           null=True,
                                           blank=True)

    # Target alphanumeric.
    alphanumeric = models.TextField(default='', blank=True)

    # Target alphanumeric color.
    alphanumeric_color = models.IntegerField(choices=Color.choices(),
                                             null=True,
                                             blank=True)

    # Free-form target description.
    description = models.TextField(default='', blank=True)

    # Uploaded target image thumbnail.
    thumbnail = models.ImageField(upload_to='targets', blank=True)

    def __unicode__(self):
        """Descriptive text for use in displays."""
        d = self.json()

        return unicode(
            "{name}(pk={id}, user={user}, "
            "target_type={type}, "
            "latitude={latitude}, "
            "longitude={longitude}, "
            "orientation={orientation}, shape={shape} "
            "background_color={background_color}, "
            "alphanumeric='{alphanumeric}', "
            "alphanumeric_color={alphanumeric_color}, "
            "description='{description}', "
            "thumbnail='{thumbnail}')".format(
                name=self.__class__.__name__,
                thumbnail=self.thumbnail, **d))

    def json(self):
        """Target as dict, for JSON."""
        target_type = None
        if self.target_type is not None:
            target_type = TargetType(self.target_type).name

        latitude = None
        longitude = None
        if self.location is not None:
            latitude = self.location.latitude
            longitude = self.location.longitude

        orientation = None
        if self.orientation is not None:
            orientation = Orientation(self.orientation).name

        shape = None
        if self.shape is not None:
            shape = Shape(self.shape).name

        background_color = None
        if self.background_color is not None:
            background_color = Color(self.background_color).name

        alphanumeric = None
        if self.alphanumeric != '':
            alphanumeric = self.alphanumeric

        alphanumeric_color = None
        if self.alphanumeric_color is not None:
            alphanumeric_color = Color(self.alphanumeric_color).name

        description = None
        if self.description != '':
            description = self.description

        return {
            'id': self.pk,
            'user': self.user.pk,
            'type': target_type,
            'latitude': latitude,
            'longitude': longitude,
            'orientation': orientation,
            'shape': shape,
            'background_color': background_color,
            'alphanumeric': alphanumeric,
            'alphanumeric_color': alphanumeric_color,
            'description': description,
        }
