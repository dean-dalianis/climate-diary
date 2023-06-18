from config import HOST, PORT, USERNAME, PASSWORD, DB_NAME, ANALYSIS_MEASUREMENTS
from influx.util import ms_to_timestamp
from influxdb import InfluxDBClient
from logging_config import logger

client = InfluxDBClient(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    database=DB_NAME
)


def fetch_data(country_id=None, measurement=None, date=None, start_date=None, end_date=None):
    """
    Fetch climate data for a specified country or all countries based on given conditions.

    :param str or None country_id: The country ID to fetch the climate data for. If None, fetch data for all countries.
    :param str or None measurement: The table name to fetch the data from. If None, fetch from all tables.
    :param str or None date: The specific date to fetch the data for. Format: 'YYYY-MM-DD'. If None, ignore date condition.
    :param str or None start_date: The start date of the range to fetch the data for. Format: 'YYYY-MM-DD'. If None, ignore start_date condition.
    :param str or None end_date: The end date of the range to fetch the data for. Format: 'YYYY-MM-DD'. If None, ignore end_date condition.
    :return: A list of records based on the specified conditions.
    :rtype: list[dict] or None
    """
    records = []

    if measurement:
        if measurement not in ANALYSIS_MEASUREMENTS:
            logger.error(f"Invalid measurement: {measurement}")
            return None
        measurement_names = [measurement]
    else:
        measurement_names = ANALYSIS_MEASUREMENTS

    for measurement in measurement_names:
        query = f'SELECT * FROM "{measurement}"'
        where_clause = []

        if country_id is not None:
            where_clause.append(f'"country_id" = \'{country_id}\'')

        if date:
            where_clause.append(f'time >= \'{date}T00:00:00Z\' AND time <= \'{date}T23:59:59Z\'')
        elif start_date and end_date:
            where_clause.append(f'time >= \'{start_date}T00:00:00Z\' AND time <= \'{end_date}T23:59:59Z\'')

        if where_clause:
            query += ' WHERE ' + ' AND '.join(where_clause)

        result = client.query(query, epoch='ms')

        if result:
            for point in result.get_points():
                record = {
                    'measurement': measurement,
                    'country_name': point['country_name'],
                    'value': point['value'],
                    'time': ms_to_timestamp(point['time'])
                }
                records.append(record)
        else:
            if date:
                logger.warning(f"No data found in DB for measurement: {measurement}, and date: {date}")
            elif start_date and end_date:
                logger.warning(
                    f"No data found in DB for measurement: {measurement}, and range: {start_date} to {end_date}")
            else:
                logger.warning(f"No data found in DB for measurement: {measurement}")

    if records:
        return records
    else:
        if date:
            logger.warning(f"No data found in DB for date: {date}")
        elif start_date and end_date:
            logger.warning(f"No data found in DB for range: {start_date} to {end_date}")
        else:
            logger.warning(f"No data found in DB")
        return None
