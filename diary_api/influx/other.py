from config import BUCKET, GSOY_MEASUREMENTS
from flask import g


def fetch_country_list():
    """
    Fetch the list of available countries.

    :return: A list of available countries.
    :rtype: list[str]
    """
    query = f'import "influxdata/influxdb/schema" schema.tagValues(bucket: "{BUCKET}", tag: "country_iso", start: 1700-01-01T00:00:00Z)'
    tables = g.query_api.query(query)
    countries = []
    for table in tables:
        for record in table.records:
            countries.append(record.get_value())
    return countries


def fetch_earliest_timestamp():
    """
    Fetch the earliest timestamp across all measurements.

    :return: The earliest timestamp as a string.
    :rtype: str or None
    """
    earliest_timestamp = None
    for table in GSOY_MEASUREMENTS:
        query = f'from(bucket: "{BUCKET}") |> range(start: 0) |> filter(fn: (r) => r["_measurement"] == "{table}") |> first(column: "_time")'
        tables = g.query_api.query(query)
        for table in tables:
            for record in table.records:
                timestamp = record.get_time()
                if earliest_timestamp is None or timestamp < earliest_timestamp:
                    earliest_timestamp = timestamp
    return earliest_timestamp.isoformat() if earliest_timestamp else None


def fetch_latest_timestamp():
    """
    Fetch the latest timestamp across all measurements.

    :return: The latest timestamp as a string.
    :rtype: str or None
    """
    latest_timestamp = None
    for table in GSOY_MEASUREMENTS:
        query = f'from(bucket: "{BUCKET}") |> range(start: 0) |> filter(fn: (r) => r["_measurement"] == "{table}") |> last(column: "_time")'
        tables = g.query_api.query(query)
        for table in tables:
            for record in table.records:
                timestamp = record.get_time()
                if latest_timestamp is None or timestamp > latest_timestamp:
                    latest_timestamp = timestamp
    return latest_timestamp.isoformat() if latest_timestamp else None


def fetch_available_measurements(country_iso=None):
    """
    Fetch the available measurements for a specified country.

    :param str country_iso: The country iso to fetch the available measurements for. If None, fetch for all countries.
    :return: A list of available measurements for the specified country or all countries.
    :rtype: list[str] or None
    """
    available_measurements = []
    for measurement in GSOY_MEASUREMENTS:
        query = f'import "influxdata/influxdb/schema" schema.measurementTagValues(bucket: "{BUCKET}", measurement: "{measurement}", tag: "country_iso", start: 1700-01-01T00:00:00Z)'
        if country_iso is not None:
            query += f'|> filter(fn: (r) => r._value == "{country_iso}")'
        tables = g.query_api.query(query)
        for table in tables:
            if len(table.records) > 0:
                available_measurements.append(measurement)
    return available_measurements if available_measurements else None


def fetch_maximum_temperature(measurement):
    """
    Fetch the maximum temperature for the specified measurement.

    :param str measurement: The measurement name to fetch the maximum temperature for.
    :return: The maximum temperature for the specified measurement.
    :rtype: float or None
    """
    max_temp = None
    query = f'from(bucket: "{BUCKET}") |> range(start: 0) |> filter(fn: (r) => r["_measurement"] == "{measurement}") |> max(column: "_value")'
    tables = g.query_api.query(query)
    for table in tables:
        for record in table.records:
            value = record.get_value()
            if max_temp is None or value > max_temp:
                max_temp = value
    return max_temp


def fetch_minimum_temperature(measurement):
    """
    Fetch the minimum temperature for the specified measurement.

    :param str measurement: The measurement name to fetch the minimum temperature for.
    :return: The minimum temperature for the specified measurement.
    :rtype: float or None
    """
    min_temp = None
    query = f'from(bucket: "{BUCKET}") |> range(start: 0) |> filter(fn: (r) => r["_measurement"] == "{measurement}") |> min(column: "_value")'
    tables = g.query_api.query(query)
    for table in tables:
        for record in table.records:
            value = record.get_value()
            if min_temp is None or value < min_temp:
                min_temp = value
    return min_temp
