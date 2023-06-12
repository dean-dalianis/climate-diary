from datetime import datetime

from dateutil.parser import parse
from dateutil.tz import tzutc


def string_to_datetime(date_string):
    """
    Parse a date string into a datetime object with timezone information.

    :param str date_string: The date string to parse, formatted as 'YYYY-MM-DD'.
    :return: A datetime object representing the parsed date, with timezone set to UTC.
    :rtype: datetime
    """
    dt = parse(date_string)
    return dt.astimezone(tzutc())


def datetime_to_string(date_time):
    """
    Format a datetime object into a string with timezone information.

    :param datetime date_time: The datetime object to format.
    :return: A string representing the formatted date, with timezone set to UTC.
    :rtype: str
    """
    return date_time.strftime('%Y-%m-%d')
