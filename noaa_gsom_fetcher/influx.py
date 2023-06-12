import json
import os
import time

from influxdb import InfluxDBClient

from logging_config import logger
from util import string_to_datetime

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

    for i in range(0, num_points, BATCHSIZE):
        current_batch_number = i // BATCHSIZE + 1
        batch_points = points[i: i + BATCHSIZE]

        if batch_points:
            try:
                logger.info(f'Writing data for {country["name"]}, batch {current_batch_number}/{num_batches}')
                client.write_points(batch_points)
                logger.info(
                    f'Successfully wrote data for {country["name"]}, batch {current_batch_number}/{num_batches}')
            except Exception as e:
                logger.error(
                    f'Failed to write data for {country["name"]}, batch {current_batch_number}/{num_batches}, {e}')
        else:
            logger.warn('No data to write')


def fetch_latest_timestamp_for_average_temperature(country):
    """
    Fetch the latest timestamp for the 'Average Temperature' for a specified country.

    :param dict country: The country to fetch the latest timestamp for.
    :return: The latest timestamp as a datetime object.
    :rtype: datetime or None
    """
    query = f"SELECT last(\"value\") FROM \"Average Temperature\" WHERE \"country\" = '{country['name']}'"
    result = client.query(query)
    if result:
        logger.info("result")
        point = list(result.get_points())[0]
        timestamp_str = point['time']
        date = string_to_datetime(timestamp_str)
        return date
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
