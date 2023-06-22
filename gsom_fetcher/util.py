import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pycountry

from logging_config import logger

LAST_RUN_LAST_RUN_FILE_PATH = "/gsom_fetcher/last_run/last_run.txt"


def string_to_datetime(date_string):
    """
    Convert a string to a datetime object. The input string should be in ISO 8601 format.

    :param str date_string: The string to convert to a datetime.
    :return: The converted datetime.
    :rtype: datetime.datetime
    """
    date_string = date_string.replace('Z', '+00:00')
    dt = datetime.fromisoformat(date_string)
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt


def datetime_to_string(dt):
    """
    Convert a datetime object to a string in ISO 8601 format.

    :param datetime.datetime dt: The datetime to convert to a string.
    :return: The datetime as a string.
    :rtype: str
    """
    return dt.astimezone(ZoneInfo("UTC")).strftime('%Y-%m-%dT%H:%M:%S')


def ms_to_timestamp(timestamp_ms):
    """
    Convert a timestamp in milliseconds to a datetime object with UTC timezone.

    :param int timestamp_ms: The timestamp in milliseconds.
    :return: The converted timestamp as a datetime object with UTC timezone.
    :rtype: datetime.datetime
    """
    timestamp = datetime.utcfromtimestamp(timestamp_ms / 1000.0)
    # Handle timestamps before 1970
    if timestamp.year < 1970:
        epoch_start = datetime(1970, 1, 1, tzinfo=timezone.utc)
        delta = timedelta(milliseconds=timestamp_ms)
        timestamp = epoch_start + delta
    return timestamp.replace(tzinfo=timezone.utc)


def should_run():
    """
     Determines if 15 days have passed since the last run.

     :return: Whether the script should run.
     :rtype: bool
     """
    from logging_config import logger

    if not os.path.exists(LAST_RUN_LAST_RUN_FILE_PATH):
        logger.info('No last_run_file found.')
        return True

    with open(LAST_RUN_LAST_RUN_FILE_PATH, "r") as f:
        last_run = datetime.strptime(f.read(), "%Y-%m-%d %H:%M:%S")

    run = datetime.now() - last_run >= timedelta(days=15)

    logger.info(f'Found last_run_file. Last run was {"less" if run is False else "more"} that 15 days ago.')
    return run


def update_last_run():
    """
    Records the current time as the 'last run' time in a file and the database.

    :return: None
    :rtype: None
    """
    current_time = datetime.now()

    last_run_point = [
        {
            "measurement": "metadata",
            "tags": {
                "script": "gsom_fetcher"
            },
            "time": current_time,
            "fields": {
                "last_run": current_time.isoformat()
            }
        }
    ]

    from influx import write_to_db
    write_to_db(last_run_point)

    with open(LAST_RUN_LAST_RUN_FILE_PATH, "w") as f:
        f.write(current_time.strftime("%Y-%m-%d %H:%M:%S"))


def get_country_alpha_2(country_name):
    try:
        alpha_2 = pycountry.countries.get(name=country_name).alpha_2
    except AttributeError:
        alpha_2 = None
        logger.warn(f'Could not get country alpha_2 for {country_name}')

    return alpha_2
