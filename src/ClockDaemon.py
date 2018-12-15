
#
# Imports
#
import RaspHTTP
import logging
import sys
from time import sleep
from enum import Enum
from RaspHTTP import Config
from LedMatrix import LedMatrix
from datetime import datetime
from service import DaemonService


#
# Constants
#
VERSION = "0.0.1"
PID_FILE = "/tmp/raspberryclock.pid"

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


class RaspberryClock(RaspHTTP.Daemon):
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


class RaspberryClockServiceDaemon(DaemonService):
    def run(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s - %(message)s')
        logging.info("Raspberry Pi Clock Daemon %s", (VERSION))
        config = RaspHTTP.Config("config.ini", DEFAULT_CONFIG)
        clock = RaspberryClock(config)
        clock.run()
        sys.exit(0)


#
# Main function
#
if __name__ == "__main__":
    daemon = RaspberryClockServiceDaemon(PID_FILE)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'run' == sys.argv[1]:
            daemon.run()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
