
#
# Imports
#
import daemonhttp
import logging.handlers
import sys
import os
from enum import Enum
from daemonhttp import Config
from ledmatrix import LedMatrix
from datetime import datetime


#
# Constants
#
VERSION = "0.0.1"
PID_FILE = "/tmp/raspberryclock.pid"
LOG_FILENAME = "/tmp/raspberryclock.log"

#
# Default configs
#

DEFAULT_CONFIG = {
    'led_intensity': '16',
    'server_port': '8080',
    'recalc_interval': '0.250',
    '24h_clock': 'false',
    'leading_zero_clock': 'false'
}


class State(Enum):
    PENDINGINIT = 1
    RUNNING = 2


class RaspberryClock(daemonhttp.Daemon):
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.now = datetime.now()
        self.state = State.PENDINGINIT
        self.ledmatrix = LedMatrix(config)
        self.prevtimestr = None;

    def api(self, api, params):
        if api == "version":
            return {
                "version": VERSION
            }

        return super().api(api, params)

    def recalculate(self):
        self.now = datetime.now()

        if self.is_state(State.PENDINGINIT):
            self.ledmatrix.display_scrolling_text("Hello!")
            self.move_state_to(State.RUNNING)

        elif self.is_state(State.RUNNING):
            self.printtime()

    def printtime(self):
        timestr = ""

        if self.config.getboolean("24h_clock"):
            if self.config.getboolean("leading_zero_clock"):
                timestr = self.now.strftime('%H:%M')
            else:
                timestr = self.now.strftime('%-H:%M')
        else:
            if self.config.getboolean("leading_zero_clock"):
                timestr = self.now.strftime('%I:%M')
            else:
                timestr = self.now.strftime('%-I:%M')

        if self.prevtimestr != timestr:
            self.ledmatrix.display_centered_text(timestr)
            self.prevtimestr = timestr

    def is_state(self, state):
        return state == self.state

    def move_state_to(self, state):
        self.state = state


#
# Main function
#
if __name__ == "__main__":
    log_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=10)
    log_handler.doRollover()
    logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s - %(message)s', handlers=[log_handler])
    logging.info("Raspberry Pi Clock Daemon %s", (VERSION))
    logging.info("Running directory is %s", (os.getcwd()))
    config = daemonhttp.Config("config.ini", DEFAULT_CONFIG)
    clock = RaspberryClock(config)
    clock.run()
    sys.exit(0)
