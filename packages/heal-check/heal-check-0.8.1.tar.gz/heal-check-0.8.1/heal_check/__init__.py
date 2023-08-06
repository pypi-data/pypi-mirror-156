import argparse
import json
import signal
import threading
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional, List

import requests
import time

from heal_check.exceptions import CheckWarning, UrlWarning, ResponseWarning, TimestampWarning, StatusWarning, DictionaryError, StatusError, WarningTimeoutError

REQUEST_TIMEOUT_DEFAULT: float = 3.05  # see https://docs.python-requests.org/en/master/user/advanced/#timeouts
HEAL_TIMEOUT_DEFAULT: float = 15
WARNING_TIMEOUT_DEFAULT: float = 600  # 10 minutes
DELAY_DEFAULT: float = 3


def _response_from_url(url: str, request_timeout: float = REQUEST_TIMEOUT_DEFAULT) -> str:
    try:
        response = requests.get(url, timeout=request_timeout)
        response.raise_for_status()
        return response.text
    except Exception as exception:
        raise UrlWarning(url, request_timeout) from exception


def _dictionary_from_response(response: str) -> dict:
    try:
        return json.loads(response)
    except Exception as exception:
        raise ResponseWarning(response) from exception


def _data_from_dictionary(dictionary: dict) -> Tuple[datetime, str, str]:
    try:
        return datetime.fromisoformat(dictionary["timestamp"]), str(dictionary["status"]), str(dictionary["mode"])
    except Exception as exception:
        raise DictionaryError(dictionary) from exception


def _check_timestamp(timestamp: datetime, heal_timeout: float = HEAL_TIMEOUT_DEFAULT, now: datetime = None) -> None:
    if not now:
        now = datetime.fromtimestamp(time.time(), timezone.utc)

    if now - timestamp > timedelta(seconds=heal_timeout):
        raise TimestampWarning(timestamp, heal_timeout, now)


def _check_status(status: str) -> None:
    if status == "fixing":
        raise StatusWarning()
    elif status != "ok":
        raise StatusError(status)


def check(url: str, request_timeout: float = REQUEST_TIMEOUT_DEFAULT, heal_timeout: float = HEAL_TIMEOUT_DEFAULT) -> str:
    response = _response_from_url(url, request_timeout)
    dictionary = _dictionary_from_response(response)
    remote_timestamp, status, mode = _data_from_dictionary(dictionary)
    _check_status(status)
    _check_timestamp(remote_timestamp, heal_timeout)

    return mode


def warning_tolerant_check(url: str,
                           event: threading.Event = None,
                           delay: float = DELAY_DEFAULT,
                           warning_timeout: float = WARNING_TIMEOUT_DEFAULT,
                           request_timeout: float = REQUEST_TIMEOUT_DEFAULT,
                           heal_timeout: float = HEAL_TIMEOUT_DEFAULT) -> str:
    if not event:
        event = threading.Event()

    timer = threading.Timer(warning_timeout, lambda: event.set())
    timer.start()

    try:
        while True:
            try:
                return check(url, request_timeout, heal_timeout)
            except CheckWarning as warning:
                event.wait(delay)
                if event.is_set():
                    raise WarningTimeoutError(warning)
    finally:
        timer.cancel()


def main(args: Optional[List[str]] = None) -> None:
    argparser = argparse.ArgumentParser(description="")
    argparser.add_argument("url", help="", metavar="<url>")
    argparser.add_argument("-d", "--delay", type=float, default=DELAY_DEFAULT, help="", metavar="<duration>")
    argparser.add_argument("-w", "--warning-timeout", type=float, default=WARNING_TIMEOUT_DEFAULT, help="", metavar="<duration>")
    argparser.add_argument("-r", "--request-timeout", type=float, default=REQUEST_TIMEOUT_DEFAULT, help="", metavar="<duration>")
    argparser.add_argument("-t", "--heal-timeout", type=float, default=HEAL_TIMEOUT_DEFAULT, help="", metavar="<duration>")
    args = argparser.parse_args(args)

    # turning SIGINT and SIGTERM into an event
    event = threading.Event()
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, lambda signum, frame: event.set())

    print(warning_tolerant_check(args.url, event, args.delay, args.warning_timeout, args.request_timeout, args.heal_timeout))
