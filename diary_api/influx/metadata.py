from config import HOST, PORT, USERNAME, PASSWORD, DB_NAME, METADATA_MEASUREMENT
from influx.util import ms_to_timestamp
from influxdb import InfluxDBClient

client = InfluxDBClient(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    database=DB_NAME,
    retries=10,
)


def fetch_last_update_time():
    """
    Fetch the latest timestamp across all measurements.

    :return: The latest timestamp as a string.
    :rtype: str or None
    """
    last_run = None

    query = f'SELECT LAST(*) FROM "{METADATA_MEASUREMENT}"'
    result = client.query(query, epoch='ms')
    if result:
        point = list(result.get_points())[0]
        timestamp_ms = point['last_last_run']
        if last_run is None or timestamp_ms > last_run:
            last_run = timestamp_ms
    return last_run
