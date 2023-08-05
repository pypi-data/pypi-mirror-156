import sys
import argparse

from powerful_pipes import report_exception, write_json_to_stdout

from .config import RunningConfig
from .brokers import connect_bus, BusInterface

def run(connection: BusInterface, config: RunningConfig):

    for message in connection.read_json_messages(config.queue_name):

        try:
            write_json_to_stdout(message, force_flush=True)

        except Exception as e:
            report_exception({}, e)


def main():
    banner = 'Powerful Pipes WatchBus tool'

    parser = argparse.ArgumentParser(
        description=banner
    )
    parser.add_argument('-b', '--banner',
                        default=False,
                        action="store_true",
                        help="displays tool banner")
    parser.add_argument('--debug',
                        default=False,
                        action="store_true",
                        help="enable debug mode")
    parser.add_argument('-c', '--bus-connection',
                        default="redis://",
                        help="bus connections. Default: 'Redis://'")

    parser.add_argument('-q', '--queue-name',
                        required=True,
                        help="bus name where listen to")

    parsed = parser.parse_args()

    config = RunningConfig.from_cli(parsed)

    if config.banner:
        print(f"[*] Starting {banner}", flush=True, file=sys.stderr)

    try:
        con = connect_bus(config.bus_connection)
    except Exception as e:
        print(e)
        exit(1)

    else:
        run(con, config)


if __name__ == '__main__':
    main()
