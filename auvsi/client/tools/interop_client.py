"""Client for interoperability. This is the sample implementation binary.

This binary brings together communication code and data generation code.

NOTE: This client is deprecated and should not be used for new tools.
"""

import argparse
import datetime
import logging
import signal
import sys
import time

import interop_comms
import interop_datagen


def signal_handler(signal, frame):
    """Handles the signal by marking the program as no longer running."""
    sys.exit(0)


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

    # Continually execute interop requests until signaled to stop
    while True:
        # Get start time of the round
        start_time = datetime.datetime.now()
        # Get UAS telemetry for round
        uas_telemetry = data_generator.get_uas_telemetry(start_time)
        (latitude, longitude, altitude_msl, uas_heading) = uas_telemetry
        # Execute interop requests
        request = interop_comms.ServerInfoRequest()
        interop_client.queue_request(request)
        request = interop_comms.ObstaclesRequest()
        interop_client.queue_request(request)
        request = interop_comms.UasTelemetryRequest(
            latitude, longitude, altitude_msl, uas_heading)
        interop_client.queue_request(request)
        # Delay for interop timing
        end_time = datetime.datetime.now()
        delay_time = interop_time - (end_time - start_time).total_seconds()
        if delay_time > 0:
            try:
                time.sleep(delay_time)
            except KeyboardInterrupt:
                sys.exit(0)


def main():
    """Configures the interoperability binary."""
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)

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
    args = parser.parse_args()

    logging.info('Interoperability server host: %s.', args.interop_server_host)
    logging.info('Interoperability time: %f.', args.interop_time)

    # Create client and data generator from parameters
    interop_client = interop_comms.InteroperabilityClient(
        args.interop_server_host)
    interop_client.daemon = True
    interop_client.start()
    data_generator = interop_datagen.ZeroValueGenerator()

    # Launch interoperability client
    run(interop_client, data_generator, args.interop_time, args.username,
        args.password)


if __name__ == '__main__':
    main()
