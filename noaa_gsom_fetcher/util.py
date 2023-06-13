from datetime import datetime
from zoneinfo import ZoneInfo


def string_to_datetime(date_string):
    """
    Convert a string to a datetime object. The input string should be in ISO 8601 format.

    :param str date_string: The string to convert to a datetime.
    :return: The converted datetime.
    :rtype: datetime.datetime
    """
    date_string = date_string.replace('Z', '+00:00')
    dt = datetime.fromisoformat(date_string)
    if dt.tzinfo is None:
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

