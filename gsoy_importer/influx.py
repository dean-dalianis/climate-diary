import time

from influxdb_client import InfluxDBClient, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from config import HOST, PORT, ORG, BUCKET, TOKEN
from logging_config import logger

client = InfluxDBClient(
    url=f'http://{HOST}:{PORT}',
    token=TOKEN,
    org=ORG,
    enable_gzip=True
)

def write_points_to_db(points, batch_size=2000):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    num_points = len(points)
    logger.debug(f'Writing {num_points} points in batches of {batch_size} to db')

    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        try:
            write_api.write(bucket=BUCKET, record=batch, write_precision=WritePrecision.MS)
        except Exception as e:
            logger.error(f'Failed to write batch {i // batch_size + 1}, {e}')
            write_api.__del__()
    write_api.__del__()


def wait_for_db():
    logger.info("Waiting for DB to be ready...")

    for i in range(30):
        try:
            client.ready()
            logger.info('DB connection successful.')
            return
        except Exception as e:
            logger.warning(
                f'Failed to connect to DB "{HOST}": ({i + 1}/30 attempts). Retrying in 1 second...',
                e)
            time.sleep(1)

    logger.error(f'Failed to connect to DB "{HOST}" after multiple attempts.')
    raise Exception(f'Cannot connect to DB: "{HOST}"')
