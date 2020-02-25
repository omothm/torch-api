"""Torch logger

Logs messages from the Torch API into a log file.
"""

__author__ = "Omar Othman"


import datetime
import os

_LOCAL_PATH = os.path.dirname(__file__)
_LOG_FILENAME = os.path.join(_LOCAL_PATH, "torch.log")


def log(tag: str, msg: str, level: str = "d"):
    """Logs the given `msg` tagged with the given `tag` having the given `level`
    to the default log file.

    ### Arguments
    `level`: could be one of
    - `v` (verbose)
    - `i` (info)
    - `d` (debug)
    - `w` (warning)
    - `e` (error)
    """
    if len(level) != 1 or level not in 'vidwe':
        raise Exception('Invalid log level')
    with open(_LOG_FILENAME, "a") as log_file:
        log_file.write(
            f"{str(datetime.datetime.now())} - {level} [{tag}] {msg}\n")


def log_e(tag: str, msg: str):
    """Logs the given `msg` tagged with the given `tag` as an error message to
    the default log file.
    """
    log(tag, msg, 'e')


def log_w(tag: str, msg: str):
    """Logs the given `msg` tagged with the given `tag` as a warning message to
    the default log file.
    """
    log(tag, msg, 'w')


def log_v(tag: str, msg: str):
    """Logs the given `msg` tagged with the given `tag` as a vebose message to
    the default log file.
    """
    log(tag, msg, 'v')


def log_i(tag: str, msg: str):
    """Logs the given `msg` tagged with the given `tag` as an information
    message to the default log file.
    """
    log(tag, msg, 'i')


def log_d(tag: str, msg: str):
    """Logs the given `msg` tagged with the given `tag` as a debug message to
    the default log file.
    """
    log(tag, msg, 'd')
