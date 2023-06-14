import datetime
import json
import os
import time

from influxdb import InfluxDBClient

from logging_config import logger
from util import string_to_datetime, ms_to_timestamp

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config/influx_config.json')
with open(CONFIG_FILE, 'r') as file:
    config = json.load(file)
HOST = config['HOST']
PORT = config['PORT']
BATCHSIZE = config['BATCHSIZE']
DB_NAME = config['DB_NAME']

USERNAME = os.environ.get('INFLUXDB_ADMIN_USER', 'admin')
PASSWORD = os.environ.get('INFLUXDB_ADMIN_PASSWORD', 'changeme')

client = InfluxDBClient(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    database=DB_NAME
)


def write_points_to_influx(points, country):
    """
    Write climate data points for a specific country to InfluxDB in batches.

    The data points are written in batches of a specified size. The function logs the progress
    of writing for each batch. If writing for a batch fails, an error message is logged.

    :param list points: The data points to write. Each data point is a dictionary.
    :param dict country: The country the data points belong to.
    :return: None
    """
    num_points = len(points)
    num_batches = (num_points + BATCHSIZE - 1) // BATCHSIZE
    logger.info(f'Writing {num_points} points in {num_batches} batches to db')
    for i in range(0, num_points, BATCHSIZE):
        current_batch_number = i // BATCHSIZE + 1
        batch_points = points[i: i + BATCHSIZE]

        if batch_points:
            try:
                client.write_points(batch_points)
                logger.info(
                    f'Successfully wrote data for {country["name"]}, batch {current_batch_number}/{num_batches}')
            except Exception as e:
                logger.error(
                    f'Failed to write data for {country["name"]}, batch {current_batch_number}/{num_batches}, {e}')
        else:
            logger.warn('No data to write')


def fetch_latest_timestamp(country):
    """
    Fetch the latest timestamp for the 'Average Temperature' for a specified country.

    :param dict country: The country to fetch the latest timestamp for.
    :return: The latest timestamp as a datetime object.
    :rtype: datetime or None
    """
    query = f"SELECT last(\"value\") FROM \"Average_Temperature\" WHERE \"country\" = '{country['name']}'"
    result = client.query(query)
    if result:
        point = list(result.get_points())[0]
        timestamp_str = point['time']
        return string_to_datetime(timestamp_str)
    return None


def fetch_climate_data_from_influx(country, datatype):
    """
    Fetch all climate data for a specified country and datatype from InfluxDB.

    :param dict country: The country to fetch the climate data for.
    :param str datatype: The datatype corresponding to a measurement in InfluxDB.
    :return: A list of records, where each record is a dictionary with 'date' and 'value'.
    :rtype: list[dict] or None
    """
    query = f"SELECT * FROM \"{datatype}\" WHERE \"country\" = '{country['name']}'"
    result = client.query(query, epoch='ms')

    if result:
        records = []
        for point in result.get_points():
            record = {
                'date': ms_to_timestamp(point['time']),
                'value': point['value']
            }
            records.append(record)
        return records
    else:
        logger.warn(f"No data found in InfluxDB for country: {country['name']} and datatype: {datatype}")
        return None


def wait_for_influx():
    """
    Wait until the InfluxDB is ready to accept connections.
    """
    logger.info("Waiting for InfluxDB to be ready...")

    for i in range(30):
        try:
            client.ping()
            logger.info('InfluxDB connection successful.')
            return
        except Exception as e:
            logger.warning(
                f'Failed to connect to InfluxDB "{HOST}:{PORT}": ({i + 1}/30 attempts). Retrying in 1 second...',
                e)
            time.sleep(1)

    logger.error(f'Failed to connect to InfluxDB "{HOST}:{PORT}" after multiple attempts.')
    raise Exception(f'Cannot connect to InfluxDB: "{HOST}:{PORT}"')


def drop_trend(country, trend):
    """
    Drop specific trend data for a specified country from InfluxDB.

    :param dict country: The country to drop the trend data for.
    :param str trend: The trend to drop.
    :return: None
    """
    try:
        query = f"DROP SERIES FROM \"{trend}\" WHERE \"country\" = '{country}'"
        client.query(query)
        logger.info(f'Successfully dropped {trend} data for {country}')
    except Exception as e:
        logger.error(f'Failed to drop {trend} data for {country}, {e}')
