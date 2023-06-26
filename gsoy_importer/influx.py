import time

from config import HOST, PORT, USERNAME, PASSWORD, DB_NAME
from influxdb import InfluxDBClient
from logging_config import logger
from util import ms_to_timestamp

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


def fetch_gsom_data_from_db(country, datatype):
    """
    Fetch all climate data for a specified country and datatype from DB.

    :param dict country: The country to fetch the climate data for.
    :param str datatype: The datatype corresponding to a measurement in DB.
    :return: A list of records, where each record is a dictionary with 'date' and 'value'.
    :rtype: list[dict] or None
    """

    query = f"SELECT * FROM \"{datatype}\" WHERE \"country_id\" = '{country['iso']}'"
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
