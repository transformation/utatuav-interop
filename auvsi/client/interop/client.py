"""Core interoperability client module

This module provides a Python interface to the SUAS interoperability API.

Users should use the AsyncClient to manage the interface, as it has performance
features. A simpler Client is also given as a base implementation.

See README.md for more details."""

from concurrent.futures import ThreadPoolExecutor
import functools
import requests
import threading

from .exceptions import InteropError
from .types import ServerInfo, StationaryObstacle, MovingObstacle


class Client(object):
    """Client which provides authenticated access to interop API.

    This client uses a single session to make blocking requests to the
    interoperability server. This is the base core implementation. The
    AsyncClient uses this base Client to add performance features.
    """

    def __init__(self, url, username, password, timeout=1):
        """Create a new Client and login.

        Args:
            url: Base URL of interoperability server
                (e.g., http://localhost:8000)
            username: Interoperability username
            password: Interoperability password
            timeout: Individual session request timeout (seconds)
        """
        self.url = url
        self.timeout = timeout

        self.session = requests.Session()

        # All endpoints require authentication, so always
        # login.
        self.post('/api/login',
                  data={'username': username,
                        'password': password})

    def get(self, uri, **kwargs):
        """GET request to server.

        Args:
            uri: Server URI to access (without base URL)
            **kwargs: Arguments to requests.Session.get method

        Raises:
            InteropError: Error from server
            requests.Timeout: Request timeout
        """
        r = self.session.get(self.url + uri, timeout=self.timeout, **kwargs)
        if not r.ok:
            raise InteropError(r)
        return r

    def post(self, uri, **kwargs):
        """POST request to server.

        Args:
            uri: Server URI to access (without base URL)
            **kwargs: Arguments to requests.Session.post method

        Raises:
            InteropError: Error from server
            requests.Timeout: Request timeout
        """
        r = self.session.post(self.url + uri, timeout=self.timeout, **kwargs)
        if not r.ok:
            raise InteropError(r)

    def get_server_info(self):
        """GET server information, to be displayed to judges.

        Returns:
            ServerInfo object

        Raises:
            InteropError: Error from server. Note that you may receive this
                error if the server has no message configured.
            requests.Timeout: Request timeout
            ValueError or AttributeError: Malformed response from server
        """
        r = self.get('/api/server_info')
        d = r.json()

        return ServerInfo(message=d['message'],
                          message_timestamp=d['message_timestamp'],
                          server_time=d['server_time'])

    def post_telemetry(self, telem):
        """POST new telemetry.

        Args:
            telem: Telemetry object containing telemetry state.

        Raises:
            InteropError: Error from server
            requests.Timeout: Request timeout
        """
        self.post('/api/telemetry', data=telem.serialize())

    def get_obstacles(self):
        """GET obstacles.

        Returns:
            List of StationaryObstacles and list of MovingObstacles.
                i.e., ([StationaryObstacle], [MovingObstacles])

        Raises:
            InteropError: Error from server
            requests.Timeout: Request timeout
            ValueError or AttributeError: Malformed response from server
        """
        r = self.get('/api/obstacles')
        d = r.json()

        stationary = []
        for o in d['stationary_obstacles']:
            s = StationaryObstacle(latitude=o['latitude'],
                                   longitude=o['longitude'],
                                   cylinder_radius=o['cylinder_radius'],
                                   cylinder_height=o['cylinder_height'])
            stationary.append(s)

        moving = []
        for o in d['moving_obstacles']:
            m = MovingObstacle(latitude=o['latitude'],
                               longitude=o['longitude'],
                               altitude_msl=o['altitude_msl'],
                               sphere_radius=o['sphere_radius'])
            moving.append(m)

        return stationary, moving


class AsyncClient(object):
    """Client which uses the base to be more performant.

    This client uses Futures with a ThreadPoolExecutor. This allows requests to
    be executed asynchronously. Asynchronous execution with multiple Clients
    enables requests to be processed in parallel and with pipeline execution at
    the server, which can drastically improve achievable interoperability rate
    as observed at the client.

    Note that methods return Future objects. Users should handle the response
    and errors appropriately. If serial request execution is desired, ensure the
    Future response or error is received prior to making another request.
    """

    def __init__(self, url, username, password, timeout=1):
        """Create a new AsyncClient and login.

        Args:
            url: Base URL of interoperability server
                (e.g., http://localhost:8000)
            username: Interoperability username
            password: Interoperability password
            timeout: Individual session request timeout (seconds)
        """
        self.client = Client(url, username, password, timeout)

        self.server_info_executor = ThreadPoolExecutor(max_workers=1)
        self.uas_telemetry_executor = ThreadPoolExecutor(max_workers=1)
        self.obstacles_executor = ThreadPoolExecutor(max_workers=1)

    def get_server_info(self):
        """GET server information, to be displayed to judges.

        Returns:
            Future object which contains the return value or error from the
            underlying Client.
        """
        return self.server_info_executor.submit(self.client.get_server_info)

    def post_telemetry(self, telem):
        """POST new telemetry.

        Args:
            telem: Telemetry object containing telemetry state.

        Returns:
            Future object which contains the return value or error from the
            underlying Client.
        """
        return self.uas_telemetry_executor.submit(self.client.post_telemetry,
                                                  telem)

    def get_obstacles(self):
        """GET obstacles.

        Returns:
            Future object which contains the return value or error from the
            underlying Client.
        """
        return self.obstacles_executor.submit(self.client.get_obstacles)
