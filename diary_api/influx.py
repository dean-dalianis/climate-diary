import datetime

from influxdb import InfluxDBClient

from config import HOST, PORT, USERNAME, PASSWORD, DB_NAME, TABLE_NAMES
from logging_config import logger
from util import string_to_datetime, ms_to_timestamp

client = InfluxDBClient(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    database=DB_NAME
)


def fetch_latest_timestamp(country):
    """
    Fetch the latest timestamp for the 'Average Temperature' for a specified country.

    :param dict country: The country to fetch the latest timestamp for.
    :return: The latest timestamp as a datetime object.
    :rtype: datetime or None
    """
    query = f"SELECT last(\"value\") FROM \"Average_Temperature\" WHERE \"country_id\" = '{country['id'].split(':')[1]}'"
    result = client.query(query)
    if result:
        point = list(result.get_points())[0]
        timestamp_str = point['time']
        return string_to_datetime(timestamp_str)
    return None


def fetch_all_data(country_id, table_name=None, date=None, start_date=None, end_date=None):
    """
    Fetch climate data for a specified country based on given conditions.

    :param str country_id: The country ID to fetch the climate data for.
    :param str table_name: The table name to fetch the data from. If None, fetch from all tables.
    :param str date: The specific date to fetch the data for. Format: 'YYYY-MM-DD'. If None, ignore date condition.
    :param str start_date: The start date of the range to fetch the data for. Format: 'YYYY-MM-DD'. If None, ignore start_date condition.
    :param str end_date: The end date of the range to fetch the data for. Format: 'YYYY-MM-DD'. If None, ignore end_date condition.
    :return: A list of records based on the specified conditions.
    :rtype: list[dict] or None
    """
    records = []

    if table_name:
        table_names = [table_name]
    else:
        table_names = TABLE_NAMES

    for table in table_names:
        query = f"SELECT * FROM \"{table}\" WHERE \"country_id\" = '{country_id}'"

        if date:
            query += f" AND time >= '{date}T00:00:00Z' AND time <= '{date}T23:59:59Z'"
        elif start_date and end_date:
            query += f" AND time >= '{start_date}T00:00:00Z' AND time <= '{end_date}T23:59:59Z'"

        result = client.query(query, epoch='ms')

        if result:
            for point in result.get_points():
                record = {
                    'table': table,
                    'value': point['value'],
                    'country_name': point['country_name'],
                    'station': point['station'],
                    'latitude': point['latitude'],
                    'longitude': point['longitude'],
                    'time': ms_to_timestamp(point['time'])
                }
                records.append(record)
        else:
            if date:
                logger.warning(f"No data found in DB for country ID: {country_id}, table: {table}, and date: {date}")
            elif start_date and end_date:
                logger.warning(f"No data found in DB for country ID: {country_id}, table: {table}, and range: {start_date} to {end_date}")
            else:
                logger.warning(f"No data found in DB for country ID: {country_id} and table: {table}")

    if records:
        return records
    else:
        if date:
            logger.warning(f"No data found in DB for country ID: {country_id} and date: {date}")
        elif start_date and end_date:
            logger.warning(f"No data found in DB for country ID: {country_id} and range: {start_date} to {end_date}")
        else:
            logger.warning(f"No data found in DB for country ID: {country_id}")
        return None
