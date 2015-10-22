"""Communication implementation for interoperability.

This handles communication with the interoperability server. This is generic and
not team specific.
"""

import abc
import datetime
import logging
import httplib
import threading
import urllib
import Queue

METHOD_GET = 'GET'
METHOD_POST = 'POST'


class InteropRequest(object):
    """Base interoperability request."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, url, method, params):
        """Inits the request with the generic params.

        Args:
            url: The url to make the request to.
            method: The method 'GET' or 'POST'.
            params: The request parameters as a dict.
        """
        # The request parameters
        self.url = url
        self.method = method
        self.params = params
        # The timing parameters
        self.queue_start_time = None
        self.queue_end_time = None
        self.request_start_time = None
        self.request_end_time = None

    def request_queued(self):
        """Marks the request as queued."""
        self.queue_start_time = datetime.datetime.now()

    def request_dequeued(self):
        """Marks the request as dequeued."""
        self.queue_end_time = datetime.datetime.now()

    def request_started(self):
        """Marks the request as started."""
        self.request_start_time = datetime.datetime.now()

    def request_finished(self):
        """Marks the request as finished."""
        self.request_end_time = datetime.datetime.now()

    def handle_response(self, client, response, status, data):
        """Handles the response of the request.

        Args:
            client: The client that executed the request.
            response: The response to handle.
            status: The status code of the response.
            data: The data of the response.
        """
        queue_time = (self.queue_end_time - self.queue_start_time
                      ).total_seconds()
        request_time = (self.request_end_time - self.request_start_time
                        ).total_seconds()
        logging.info(
            'Url: %s. Method: %s. Params: %s. Status: %s. Data: %s. '
            'Queue Time: %s. Request Time: %s.', self.url, self.method,
            str(self.params), status, data, queue_time, request_time)


class LoginRequest(InteropRequest):
    """A login request for interoperability."""

    def __init__(self, username, password):
        """Inits a login request with credentials.

        Args:
            username: The username to login with.
            password: The password to login with.
        """
        url = '/api/login'
        method = METHOD_POST
        params = {'username': username, 'password': password, }

        super(LoginRequest, self).__init__(url, method, params)

    def handle_response(self, client, response, status, data):
        """Overrides base method."""
        super(LoginRequest, self).handle_response(
            client, response, status, data)
        client.cookies = response.getheader('Set-Cookie')


InteropRequest.register(LoginRequest)


class ServerInfoRequest(InteropRequest):
    """A request for server information."""

    def __init__(self):
        """Inits the server info request."""
        url = '/api/server_info'
        method = METHOD_GET
        params = {}
        super(ServerInfoRequest, self).__init__(url, method, params)


InteropRequest.register(ServerInfoRequest)


class ObstaclesRequest(InteropRequest):
    """A request for obstalce information."""

    def __init__(self):
        """Inits the obstacle info request."""
        url = '/api/obstacles'
        method = METHOD_GET
        params = {}
        super(ObstaclesRequest, self).__init__(url, method, params)


InteropRequest.register(ObstaclesRequest)


class UasTelemetryRequest(InteropRequest):
    """A request to upload UAS telemetry."""

    def __init__(self, latitude, longitude, altitude_msl, uas_heading):
        """Inits the UAS telemetry request with UAS state.

        Args:
            latitude: The latitude in degrees.
            longitude: The longitude in degrees.
            altitude_msl: The altitude in feet.
            uas_heading: The UAS heading in degrees.
        """
        url = '/api/telemetry'
        method = METHOD_POST
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'altitude_msl': altitude_msl,
            'uas_heading': uas_heading,
        }
        super(UasTelemetryRequest, self).__init__(url, method, params)


InteropRequest.register(UasTelemetryRequest)


class InteroperabilityClient(threading.Thread):
    """Interoperability client which can make requests async."""

    def __init__(self, host, max_queued=30):
        """Creates a client with the given host.

        Args:
            host: A string host. This is the hostname and port (localhost:80)
            max_queued: The max number of requests that can be queued before
                blocking.
        """
        super(InteroperabilityClient, self).__init__()
        self.conn = httplib.HTTPConnection(host)
        self.requests = Queue.Queue(maxsize=max_queued)
        self.cookies = None

    def queue_request(self, interop_request):
        """Queues the request for processing. Blocks if full.

        Args:
            interop_request: The request to queue for execution.
        """
        assert isinstance(interop_request, InteropRequest)
        interop_request.request_queued()
        self.requests.put(interop_request)

    def run(self):
        """The processing function for requests."""
        while True:
            # Get request to make
            cur_request = self.requests.get()
            cur_request.request_dequeued()
            headers = {}
            # Set cookies (e.g. session info)
            if self.cookies:
                headers['Cookie'] = self.cookies
            # Make request
            if cur_request.method == METHOD_GET:
                url = (cur_request.url + '?' +
                       urllib.urlencode(cur_request.params))
                self.conn.request(cur_request.method, url, headers=headers)
            else:
                headers['Content-type'] = 'application/x-www-form-urlencoded'
                self.conn.request(
                    cur_request.method, cur_request.url,
                    urllib.urlencode(cur_request.params), headers)
            cur_request.request_started()
            # Get response
            response = self.conn.getresponse()
            # Handle response
            status = response.status
            data = response.read()
            cur_request.request_finished()
            cur_request.handle_response(self, response, status, data)
