from interop_datagen import DataGenerator
from xml.etree import ElementTree
from LatLon.lat_lon import LatLon

switch_threshold = 15  # Meters
max_turn_rate = 120  # Degrees per second
max_climb_rate = 10  # Meters per second


class KmlGenerator(DataGenerator):
    def __init__(self, filename):
        self.path = _read_kml_flightpath(filename)
        self.speed = 50  # Meters per second
        self.time = None
        self.waypoint = 0
        self.pos = self.path[self.waypoint]
        self.waypoint = 1

    def start(self, start_time):
        self.time = start_time

    def get_uas_telemetry(self, new_time):
        delta_time = (new_time - self.time).total_seconds()
        self.time = new_time
        move_distance = self.speed * delta_time

        delta_altitude = delta_time * max_climb_rate
        delta_heading = delta_time * max_turn_rate

        while move_distance > 0:
            vec = self.pos.vector(self.path[self.waypoint])

            # Way-point Switching
            if vec.distance < switch_threshold:
                if self.waypoint + 1 == len(self.path):
                    break
                else:
                    self.waypoint += 1
                    continue

            # Climb as needed
            vec.altitude = max(vec.altitude, -delta_altitude)
            vec.altitude = min(vec.altitude, delta_altitude)
            delta_altitude -= abs(vec.altitude)

            # Turn as needed
            vec.vector.heading, delta_heading = calc_new_heading(
                self.pos.heading, vec.heading, delta_heading)

            vec.distance = move_distance if vec.distance > move_distance else vec.distance
            move_distance -= vec.distance

            # Apply motion
            self.pos.move(vec)

        return (
            self.pos.latitude, self.pos.longitude, self.pos.altitude,
            self.pos.heading, )


def calc_new_heading(current, commanded, max_delta):
    def get_angle(a, b):
        b = b if b < a else b + 360
        return (b - a) % 360

    # Select the shortest direction to turn
    cw_turn = get_angle(current, commanded)
    ccw_turn = get_angle(commanded, current)
    turn = min(cw_turn, ccw_turn)

    # Limit turn magnitude
    turn = min(turn, max_delta)
    max_delta -= turn

    # Set Turn Sign
    if ccw_turn < cw_turn:
        turn = -turn

    # Add turn to current heading
    turn = (turn + current) % 360

    return turn, max_delta


def _read_kml_flightpath(filename):
    """
    Reads a .kml file that contains a Placemark with name "FlightPath" and has a LineString object
    :param filename: KML File to import
    :type filename: str
    :return: List of coordinate tuples (lat, lon, alt)
    :rtype: list[()]
    """
    with open(filename, 'rt') as f:
        tree = ElementTree.parse(f)

    correct_name = False
    coords = None
    for node in tree.iter('{http://www.opengis.net/kml/2.2}Placemark'):
        for name in node.iter('{http://www.opengis.net/kml/2.2}name'):
            if name.text.strip() == 'FlightPath':
                correct_name = True
            if not correct_name:
                continue
        for line_string in node.iter(
            '{http://www.opengis.net/kml/2.2}LineString'):
            for coordinates in line_string.iter(
                '{http://www.opengis.net/kml/2.2}coordinates'):
                coords = coordinates.text.strip()
                break
    if coords is None:
        raise AttributeError

    # Coords is a space delimited string of comma delimited floats
    # i.e.  -76.42769387747484,38.14568798598072,0 -76.42978051879199,38.15063018032259,30 ...
    coord_list = map(lambda pos_str: pos_str.split(','), coords.split(' '))  # Split into list of strings
    coord_list = [map(float, x) for x in coord_list]  # Convert strings to floats
    return [SpatialState(x[1], x[0], x[2]) for x in coord_list]  # Convert to list of tuples


class SpatialState(object):
    def __init__(self, lat, lon, alt, heading=0):
        self._latlon = LatLon(lat, lon)
        self._alt = alt
        self._heading = heading

    @property
    def altitude(self):
        return self._alt

    @property
    def latitude(self):
        return self._latlon.lat.decimal_degree

    @property
    def longitude(self):
        return self._latlon.lon.decimal_degree

    @property
    def heading(self):
        return self._heading

    def vector(self, waypoint):
        """
        :type waypoint: SpatialState
        """
        movevec = self._latlon - waypoint._latlon
        return SpatialVector(
            vector=movevec,
            altitude=waypoint._alt - self._alt, )

    def move(self, vec):
        """
        :type vec: SpacialVector
        """
        self._latlon -= vec.vector
        self._alt += vec.altitude
        self._heading = vec.heading

    def __str__(self):
        return 'Position ({}) Altitude {}m Heading{} degrees'\
            .format(self._latlon.lat(), self._latlon.lon(), self._alt, self._heading)


class SpatialVector(object):
    def __init__(self, vector, altitude):
        self.vector = vector
        self.altitude = altitude

    @property
    def distance(self):
        return self.vector.magnitude * 1000

    @distance.setter
    def distance(self, value):
        self.vector.magnitude = value / 1000.0

    @property
    def heading(self):
        return self.vector.heading

    @heading.setter
    def heading(self, value):
        self.vector.heading = value
