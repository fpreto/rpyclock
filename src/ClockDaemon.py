
#
# Imports
#
import RaspHTTP
import logging
import RaspberryPi
import sys

#
# Constants
#
from RaspHTTP import Config

VERSION = "0.0.1"

#
# Default configs
#

DEFAULT_CONFIG = {
    'server_port': '8080',
    'recalc_interval': '0.250'
}


class RaspberryClock(RaspHTTP.Daemon):

    def __init__(self, config: Config) -> None:
        super().__init__(config)


    def api(self, api, params):
        if api == "version":
            return {
                "version": VERSION
            }

        return super().api(api, params)

    def recalculate(self):
        pass


#
# Main function
#
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s - %(message)s')
    logging.info("Raspberry Pi Clock Daemon %s", (VERSION))
    config = RaspHTTP.Config("config.ini", DEFAULT_CONFIG)
    daemon = RaspberryClock(config)
    daemon.run()
    sys.exit(0)
