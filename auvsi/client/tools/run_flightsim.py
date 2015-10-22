""" Runs the Mission Simulator """

import argparse
import datetime
import logging
import sys
import time

import interop_comms
from flightsim import KmlGenerator


def run(interop_client, data_generator, interop_time, username, password):
    """Executes interoperability using the given configuration.

    Args:
        interop_client: The communication client.
        data_generator: The generator of UAS telemetry.
        interop_time: The time between interoperability execution.
        username: The username for the client.
        password: The password for the client.
    """
    # Start by logging in the client
    request = interop_comms.LoginRequest(username, password)
    interop_client.queue_request(request)

    #Start simulator
    data_generator.start(datetime.datetime.now())

    # Continually execute interop requests
    for sim_time in sim_frames(interop_time):
        # Execute server info requests
        request = interop_comms.ServerInfoRequest()
        interop_client.queue_request(request)

        # Execute interop requests
        request = interop_comms.ObstaclesRequest()
        interop_client.queue_request(request)

        # Get UAS telemetry
        uas_telemetry = data_generator.get_uas_telemetry(sim_time)
        request = interop_comms.UasTelemetryRequest(*uas_telemetry)
        interop_client.queue_request(request)


def sim_frames(interop_time):
    start_time = datetime.datetime.now()
    while True:
        yield datetime.datetime.now()
        start_time += datetime.timedelta(0, interop_time)
        delay_time = (start_time - datetime.datetime.now()).total_seconds()
        if delay_time > 0:
            time.sleep(delay_time)


def main():
    """Configures the interoperability binary."""
    # Setup logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s. %(name)s. %(levelname)s. %(message)s')
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    # Get parameters from command line
    parser = argparse.ArgumentParser(
        description='Sample interoperability implementation.')
    parser.add_argument(
        'interop_server_host',
        metavar='H',
        type=str,
        nargs='?',
        help='Host and port of interoperability server. E.g. localhost:80')
    parser.add_argument(
        'interop_time',
        metavar='T',
        type=float,
        nargs='?',
        help='Time between interoperability request sets. Floating point '
        'seconds.')
    parser.add_argument('username',
                        metavar='U',
                        type=str,
                        nargs='?',
                        help='Username for interoperability login.')
    parser.add_argument('password',
                        metavar='P',
                        type=str,
                        nargs='?',
                        help='Password for interoperability login.')
    parser.add_argument('kml',
                        metavar='K',
                        type=str,
                        nargs='?',
                        help='KML File containing mission plan')
    args = parser.parse_args()

    logging.info('Interoperability server host: %s.', args.interop_server_host)
    logging.info('Interoperability time: %f.', args.interop_time)

    # Create client and data generator from parameters
    interop_client = interop_comms.InteroperabilityClient(
        args.interop_server_host)
    interop_client.start()
    data_generator = KmlGenerator(args.kml)

    # Launch interoperability client
    run(interop_client, data_generator, args.interop_time, args.username,
        args.password)


if __name__ == '__main__':
    main()
