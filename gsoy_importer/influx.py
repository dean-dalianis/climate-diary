import time

from config import HOST, PORT, USERNAME, PASSWORD, DB_NAME
from influxdb import InfluxDBClient
from logging_config import logger

client = InfluxDBClient(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    database=DB_NAME
)


def write_points_to_db(points):
    """
    Write climate data points to InfluxDB.

    :param list points: The data points to write. Each data point is a dictionary.
    :return: None
    :rtype: None
    """
    num_points = len(points)
    logger.debug(f'Writing {num_points} points in batches to db')

    try:
        client.write_points(points)
    except Exception as e:
        logger.error(f'Failed to write data, {e}')

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


def drop(country_id, measurement):
    """
    Drop specific trend data for a specified country from DB.

    :param str country_id: The country id to drop the measurement data for.
    :param str measurement: The measurement to drop.
    :return: None
    :rtype: None
    """
    try:
        query = f"DROP SERIES FROM \"{measurement}\" WHERE \"country_id\" = '{country_id}'"
        client.query(query)
        logger.debug(f'Successfully dropped {measurement} data for {country_id}')
    except Exception as e:
        logger.warning(f'Failed to drop {measurement} data for {country_id}, {e}')
