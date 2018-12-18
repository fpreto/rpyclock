
"""
RaspberryPI Linux Hardware Interface

This module allows to interface with RaspberryPI hardware when running on a Raspbian Linux.
"""

#
# Imports
#
import os
import re
import apt
import http.client
import json
import urllib.request
import datetime
import dateutil.parser
import pytz

apt_cache = None


#
# Code Implementation
#
def readcmd(cmd: str, multiline = False):
    """Read command and get the output as a string or list of string based on the multiline parameter.

    Parameters
    ----------
    cmd : str
        The command to execute in the console
    multiline: bool
        Should get all the lines as a list of string or just the first line
    """
    with os.popen(cmd) as process:
        if multiline:
            return [line.rstrip('\n') for line in process]
        else:
            return process.readline().rstrip('\n')


def readjson(url: str) -> dict:
    return json.loads(urllib.request.urlopen(url).read().decode("utf-8"))


def check_package(package: str, refreshcache = False) -> str:
    global apt_cache
    if refreshcache or apt_cache == None:
        apt_cache = apt.Cache()

    return package in apt_cache and apt_cache[package].is_installed


def get_temperature():
    return float(re.search(r'temp=([0-9]+[\.]*[0-9]+)\'C', readcmd('vcgencmd measure_temp')).group(1))


def get_voltage():
    return float(re.search(r'volt=([0-9]+[\.]*[0-9]+)V', readcmd('vcgencmd measure_volts')).group(1))


def get_frequency():
    return int(readcmd('vcgencmd measure_clock arm').split('=')[1])


def get_totalmemory():
    with open('/proc/meminfo', 'r') as meminfo:
        total_line = list(filter(lambda s: s.startswith('MemTotal:'), meminfo))[0]
        total_value = re.findall(r'([0-9]+)\s', total_line)[0]
        return int(total_value)


def get_freememory():
    with open('/proc/meminfo', 'r') as meminfo:
        total_line = list(filter(lambda s: s.startswith('MemFree:'), meminfo))[0]
        total_value = re.findall(r'([0-9]+)\s', total_line)[0]
        return int(total_value)


def get_uptime():
    with open('/proc/uptime', 'r') as uptime:
        return float(uptime.readline().split()[0])


def get_loadavg(metric=2):
    with open('/proc/loadavg', 'r') as loadavg:
        return float(loadavg.readline().split()[metric])


def get_ssid():
    """
    Get the wifi SSID. If no connection is available then return None
    """
    wid = readcmd("iwgetid")
    if "ESSID" in wid:
        return re.search(r'.*ESSID:\"(.*)\"', wid).group(1)
    else:
        return None


def check_internet(url="www.google.com"):
    conn = http.client.HTTPConnection(url, timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except (http.client.HTTPException, IOError, OSError) as error:
        conn.close()
        return False


def get_external_ip():
    response = readjson('https://api.ipify.org/?format=json')
    return response['ip']


def get_geolocation(ip):
    return readjson('http://ip-api.com/json/%s' % ip)


def get_geolocation_data(ip=None, timezone=None):
    if not ip:
        ip = get_external_ip()
    geodata = readjson('http://ip-api.com/json/%s' % ip)
    sundata = readjson(
        'https://api.sunrise-sunset.org/json?lat=%s&lng=%s&formatted=0' % (geodata['lat'], geodata['lon']))

    if not timezone:
        timezone = pytz.timezone(geodata['timezone'])

    sunrise = dateutil.parser.parse(sundata['results']['sunrise']).astimezone(timezone)
    sunset = dateutil.parser.parse(sundata['results']['sunset']).astimezone(timezone)

    response = {
        'date': datetime.now(timezone).date(),
        'ip': ip,
        'city': geodata['city'],
        'country': geodata['country'],
        'state': geodata['regionName'],
        'countryCode': geodata['countryCode'],
        'timezone': timezone,
        'sunrise': sunrise,
        'sunset': sunset
    }

    return response

