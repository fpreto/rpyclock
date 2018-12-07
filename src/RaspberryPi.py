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


def check_package(package: str, refreshcache = False) -> str:
    global apt_cache
    if refreshcache or apt_cache == None:
        apt_cache = apt.Cache()

    return package in apt_cache and apt_cache[package].is_installed


def get_temperature():
    return re.search(r'temp=([0-9]+[\.]*[0-9]+)\'C', readcmd('vcgencmd measure_temp')).group(1)


def get_voltage():
    return re.search(r'volt=([0-9]+[\.]*[0-9]+)V', readcmd('vcgencmd measure_volts')).group(1)


def get_frequency():
    return readcmd('vcgencmd measure_clock arm').split('=')[1]


def get_totalmemory():
    with open('/proc/meminfo', 'r') as meminfo:
        total_line = list(filter(lambda s: s.startswith('MemTotal:'), meminfo))[0]
        total_value = re.findall(r'([0-9]+)\s', total_line)[0]
        return total_value


def get_freememory():
    with open('/proc/meminfo', 'r') as meminfo:
        total_line = list(filter(lambda s: s.startswith('MemFree:'), meminfo))[0]
        total_value = re.findall(r'([0-9]+)\s', total_line)[0]
        return total_value


def get_uptime():
    with open('/proc/uptime', 'r') as uptime:
        return uptime.readline().split()[0]


def get_loadavg(metric=2):
    with open('/proc/loadavg', 'r') as loadavg:
        return loadavg.readline().split()[metric]
