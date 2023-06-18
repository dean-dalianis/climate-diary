from config import HOST, PORT, USERNAME, PASSWORD, DB_NAME, DEFAULT_MEASUREMENTS, ANALYSIS_MEASUREMENTS, \
    TRENDS_MEASUREMENTS
from influx.util import ms_to_timestamp
from influxdb import InfluxDBClient

client = InfluxDBClient(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    database=DB_NAME,
    retries=10,
)


def fetch_country_list():
    """
    Fetch the list of available countries.

    :return: A list of available countries.
    :rtype: list[str]
    """
    countries = []
    query = f"SHOW TAG VALUES WITH KEY = \"country_id\""
    result = client.query(query)
    if result:
        for point in result.get_points():
            if point['value'] not in countries:
                countries.append(point['value'])

    return countries


def fetch_latest_timestamp():
    """
    Fetch the latest timestamp across all measurements.

    :return: The latest timestamp as a string.
    :rtype: str or None
    """
    latest_timestamp = None
    for table in DEFAULT_MEASUREMENTS:
        query = f'SELECT last("value") FROM "{table}"'
        result = client.query(query, epoch='ms')
        if result:
            point = list(result.get_points())[0]
            timestamp_ms = point['time']
            if latest_timestamp is None or timestamp_ms > latest_timestamp:
                latest_timestamp = timestamp_ms
    return ms_to_timestamp(latest_timestamp) if latest_timestamp else None


def fetch_earliest_timestamp():
    """
    Fetch the earliest timestamp across all measurements.

    :return: The earliest timestamp as a string.
    :rtype: str or None
    """
    earliest_timestamp = None
    for table in DEFAULT_MEASUREMENTS:
        query = f'SELECT first("value") FROM "{table}"'
        result = client.query(query, epoch='ms')
        if result:
            point = list(result.get_points())[0]
            timestamp_ms = point['time']
            if earliest_timestamp is None or timestamp_ms < earliest_timestamp:
                earliest_timestamp = timestamp_ms
    return ms_to_timestamp(earliest_timestamp) if earliest_timestamp else None


def fetch_available_measurements(country_id=None):
    """
    Fetch the available measurements for a specified country.

    :param str country_id: The country ID to fetch the available measurements for. If None, fetch for all countries.
    :return: A list of available measurements for the specified country or all countries.
    :rtype: list[str] or None
    """
    available_measurements = []
    all_measurements = DEFAULT_MEASUREMENTS + ANALYSIS_MEASUREMENTS + TRENDS_MEASUREMENTS

    for measurement in all_measurements:
        query = f"SHOW TAG VALUES FROM \"{measurement}\" WITH KEY = \"country_id\""
        if country_id is not None:
            query += f" WHERE \"country_id\" = '{country_id}'"
        result = client.query(query)
        if result:
            for point in result.get_points():
                if measurement not in available_measurements:
                    available_measurements.append(measurement)
    return available_measurements if available_measurements else None
