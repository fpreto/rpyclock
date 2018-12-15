
#
# Imports
#
import configparser
import json
import logging
import RaspberryPi
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs


class Config:
    def __init__(self, filename, default={}):
        self.filename = filename
        self.default = default
        self.config = configparser.ConfigParser()

    def load(self):
        self.config.read(self.filename)
        if 'DEFAULT' not in self.config:
            self.config['DEFAULT'] = {}

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)

    def getint(self, key):
        if self.config.has_option('DEFAULT', key):
            return self.config.getint('DEFAULT', key)
        else:
            return int(self.default[key])

    def getboolean(self, key):
        if self.config.has_option('DEFAULT', key):
            return self.config.getboolean('DEFAULT', key)
        else:
            return self.default[key].lower() in ['true', '1', 't', 'y', 'yes', 'on']

    def __getitem__(self, key):
        if key in self.config['DEFAULT']:
            return self.config['DEFAULT'][key]
        else:
            return self.default[key]

    def __setitem__(self, key, value):
        self.config['DEFAULT'][key] = str(value)


class DaemonHTTPHandler(SimpleHTTPRequestHandler):
    def do_GET(self):

        if DaemonHTTPHandler._is_resource_access(self.path):
            SimpleHTTPRequestHandler.do_GET(self)

        elif DaemonHTTPHandler._is_api_request(self.path):
            self._handle_api()

        else:
            logging.error("Invalid resource access %s", self.path)
            self.send_error(404, "Resource not found")

    def log_message(self, format, *args):
        logging.info("%s %s", self.address_string(), format % args)

    def log_error(self, format, *args):
        logging.error("%s %s", self.address_string(), format % args)

    def translate_path(self, path):
        if path.startswith('/resources'):
            return super().translate_path(path)
        else:
            return super().translate_path("/resources" + path)

    def _handle_api(self):
        # Parse URL
        parsed_url = urlparse(self.path)
        api = parsed_url.path[len("/api/"):].lower()
        query_params = parse_qs(parsed_url.query)

        # Retrieve API Data
        data = self.server.daemon.handle_api(api, query_params, None)

        # If API data is valid then send it
        if data:
            encoded_data = bytes(data, "UTF-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Length", len(encoded_data))
            self.end_headers()

            self.wfile.write(encoded_data)
        else:
            logging.error("Invalid API call. API: %s", api)
            self.send_error(500, "Not implemented")

    @staticmethod
    def _is_api_request(path: str) -> bool:
        if path.startswith("/api") and len(path) > len("/api/"):
            return True
        else:
            return False

    @staticmethod
    def _is_resource_access(path: str) -> bool:
        if path.startswith("/resources"):
            return True
        if path == "/index.html" or path == "/":
            return True
        return False


class Daemon:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.config.load()
        self.recalc_interval = float(self.config['recalc_interval'])
        self.http_server = HTTPServer(('', self.config.getint('server_port')), DaemonHTTPHandler)
        self.http_server.daemon = self
        self.http_server_thread = threading.Thread(target=self.http_server.serve_forever)

    def handle_api(self, api, query, post) -> str:
        logging.info("API Request handling. API:%s QUERY:%s POST:%s", api, query, post)

        param = {}
        if query:
            param.update(query)
        if post:
            param.update(post)

        result = self.api(api, param)

        return json.dumps(result)

    def api(self, api, params):
        result = {}

        if api == "hardware":
            result['temperature'] = RaspberryPi.get_temperature()
            result['voltage'] = RaspberryPi.get_voltage()
            result['frequency'] = RaspberryPi.get_frequency()
            result['memory'] = RaspberryPi.get_totalmemory()
            result['free'] = RaspberryPi.get_freememory()
            result['uptime'] = RaspberryPi.get_uptime()
            result['loadavg'] = RaspberryPi.get_loadavg()
        else:
            return None

        return result

    def run(self):
        try:
            logging.info("Starting server at %s...", "%s:%s" % self.http_server.server_address)
            self.http_server_thread.start()
            while True:
                logging.debug("Recalculating...")
                self.recalculate()
                logging.debug("... finished recalculating")
                time.sleep(self.recalc_interval)
        except KeyboardInterrupt:
            logging.info("Shutting down server...")
            self.http_server.shutdown()

        self.http_server_thread.join()
        logging.info("bye!")

    def recalculate(self):
        pass

