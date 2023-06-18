from config import HOST, PORT, USERNAME, PASSWORD, DB_NAME, TRENDS_MEASUREMENTS
from influxdb import InfluxDBClient
from logging_config import logger

client = InfluxDBClient(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    database=DB_NAME
)


def fetch_data(country_id=None, measurement=None):
    """
    Fetch the latest climate data for a specified country or all countries based on given conditions.

    :param str or None country_id: The country ID to fetch the climate data for. If None, fetch data for all countries.
    :param str or None measurement: The table name to fetch the data from. If None, fetch from all tables.
    :return: A single record containing the latest data based on the specified conditions.
    :rtype: dict or None
    """
    if measurement:
        if measurement not in TRENDS_MEASUREMENTS:
            logger.error(f"Invalid measurement: {measurement}")
            return None
        measurement_names = [measurement]
    else:
        measurement_names = TRENDS_MEASUREMENTS

    latest_data = None

    for measurement in measurement_names:
        query = f'SELECT LAST(*) FROM "{measurement}"'
        where_clause = []

        if country_id is not None:
            where_clause.append(f'"country_id" = \'{country_id}\'')

        if where_clause:
            query += ' WHERE ' + ' AND '.join(where_clause)

        result = client.query(query, epoch='ms')

        if result:
            points = list(result.get_points())
            if points:
                latest_point = points[0]
                latest_data = {
                    'measurement': measurement,
                    'country_name': latest_point['country_name'],
                    'slope': latest_point['slope'],
                    'intercept': latest_point['intercept']
                }
            else:
                logger.warning(f"No data found in DB for measurement: {measurement}")
        else:
            logger.warning(f"No data found in DB for measurement: {measurement}")

    if latest_data:
        return latest_data
    else:
        logger.warning(f"No data found in DB")
        return None
