import datetime
import time

from influxdb import InfluxDBClient

from config import HOST, PORT, USERNAME, PASSWORD, DB_NAME, BATCHSIZE
from logging_config import logger
from util import string_to_datetime, ms_to_timestamp

client = InfluxDBClient(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    database=DB_NAME
)


def write_points_to_db(points, country):
    """
    Write climate data points for a specific country to DB in batches.

    The data points are written in batches of a specified size. The function logs the progress
    of writing for each batch. If writing for a batch fails, an error message is logged.

    :param list points: The data points to write. Each data point is a dictionary.
    :param dict country: The country the data points belong to.
    :return: None
    :rtype: None
    """
    num_points = len(points)
    num_batches = (num_points + BATCHSIZE - 1) // BATCHSIZE
    logger.info(f'Writing {num_points} points in {num_batches} batches to db')
    for i in range(0, num_points, BATCHSIZE):
        current_batch_number = i // BATCHSIZE + 1
        batch_points = points[i: i + BATCHSIZE]

        if batch_points:
            try:
                write_to_db(batch_points)
                logger.info(
                    f'Successfully wrote data for {country["name"]}, batch {current_batch_number}/{num_batches}')
            except Exception as e:
                logger.error(
                    f'Failed to write data for {country["name"]}, batch {current_batch_number}/{num_batches}, {e}')
        else:
            logger.warning('No data to write')


def write_to_db(points):
    """
    Write a list of points to the database.

    :param points: the list of points to be written in the database
    :return: None
    :rtype: None
    """
    client.write_points(points)


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


def fetch_gsom_data_from_db(country, datatype):
    """
    Fetch all climate data for a specified country and datatype from DB.

    :param dict country: The country to fetch the climate data for.
    :param str datatype: The datatype corresponding to a measurement in DB.
    :return: A list of records, where each record is a dictionary with 'date' and 'value'.
    :rtype: list[dict] or None
    """
    query = f"SELECT * FROM \"{datatype}\" WHERE \"country_id\" = '{country['id'].split(':')[1]}'"
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
        logger.warning(f"No data found in DB for country: {country['name']} and datatype: {datatype}")
        return None


def wait_for_db():
    """
    Wait until the DB is ready to accept connections.

    :return: None
    :rtype: None
    """
    logger.info("Waiting for DB to be ready...")

    for i in range(30):
        try:
            client.ping()
            logger.info('DB connection successful.')
            return
        except Exception as e:
            logger.warning(
                f'Failed to connect to DB "{HOST}:{PORT}": ({i + 1}/30 attempts). Retrying in 1 second...',
                e)
            time.sleep(1)

    logger.error(f'Failed to connect to DB "{HOST}:{PORT}" after multiple attempts.')
    raise Exception(f'Cannot connect to DB: "{HOST}:{PORT}"')


def drop(country, measurement):
    """
    Drop specific trend data for a specified country from DB.

    :param dict country: The country to drop the measurement data for.
    :param str measurement: The measurement to drop.
    :return: None
    :rtype: None
    """
    try:
        query = f"DROP SERIES FROM \"{measurement}\" WHERE \"country\" = '{country}'"
        client.query(query)
        logger.info(f'Successfully dropped {measurement} data for {country}')
    except Exception as e:
        logger.warning(f'Failed to drop {measurement} data for {country}, {e}')
