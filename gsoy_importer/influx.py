import time

from influxdb_client import InfluxDBClient, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from config import HOST, PORT, USERNAME, PASSWORD, ORG, BUCKET
from logging_config import logger
from util import ms_to_timestamp

client = InfluxDBClient(
    url=f'http://{HOST}:{PORT}',
    username=USERNAME,
    password=PASSWORD,
    org=ORG,
    enable_gzip=True,
)

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()


def write_points_to_db(points):
    num_points = len(points)
    logger.debug(f'Writing {num_points} points in batches to db')

    try:
        write_api.write(bucket=BUCKET, record=points, write_precision=WritePrecision.MS)
    except Exception as e:
        logger.error(f'Failed to write data, {e}')


def fetch_gsom_data_from_db(country, datatype):
    query = f'from(bucket: "{BUCKET}") |> filter(fn: (r) => r._measurement == "{datatype}" and r.country_id == "{country["iso"]}")'
    result = query_api.query(query)

    if result:
        records = []
        for table in result:
            for row in table.records:
                record = {
                    'date': ms_to_timestamp(row.get_time()),
                    'value': row.get_value()
                }
                records.append(record)
        return records
    else:
        logger.warning(f"No data found in DB for country: {country['name']} and datatype: {datatype}")
        return None


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
