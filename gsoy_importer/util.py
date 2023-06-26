import os
import tarfile
import urllib
from datetime import datetime, timedelta, timezone

LAST_RUN_LAST_RUN_FILE_PATH = "/last_run/last_run.txt"
GSOY_DOWNLOAD_URL = "https://www.ncei.noaa.gov/data/gsoy/archive/gsoy-latest.tar.gz"


def should_run():
    """
     Determines if 15 days have passed since the last run.

     :return: Whether the script should run.
     :rtype: bool
     """
    from logging_config import logger

    if not os.path.exists(LAST_RUN_LAST_RUN_FILE_PATH):
        logger.info('No last_run_file found.')
        return True

    with open(LAST_RUN_LAST_RUN_FILE_PATH, "r") as f:
        last_run = datetime.strptime(f.read(), "%Y-%m-%d %H:%M:%S")

    run = datetime.now() - last_run >= timedelta(days=15)

    logger.info(f'Found last_run_file. Last run was {"less" if run is False else "more"} that 15 days ago.')
    return run


def ms_to_timestamp(timestamp_ms):
    """
    Convert a timestamp in milliseconds to a datetime object with UTC timezone.

    :param int timestamp_ms: The timestamp in milliseconds.
    :return: The converted timestamp as a datetime object with UTC timezone.
    :rtype: datetime.datetime
    """
    timestamp = datetime.utcfromtimestamp(timestamp_ms / 1000.0)
    # Handle timestamps before 1970
    if timestamp.year < 1970:
        epoch_start = datetime(1970, 1, 1, tzinfo=timezone.utc)
        delta = timedelta(milliseconds=timestamp_ms)
        timestamp = epoch_start + delta
    return timestamp.replace(tzinfo=timezone.utc)


def update_last_run():
    """
    Records the current time as the 'last run' time in a file and the database.

    :return: None
    :rtype: None
    """
    current_time = datetime.now()

    last_run_point = [
        {
            "measurement": "metadata",
            "tags": {
                "script": "gsoy_importer"
            },
            "time": current_time,
            "fields": {
                "last_run": current_time.isoformat()
            }
        }
    ]

    from gsoy_importer.influx import write_points_to_db
    write_points_to_db(last_run_point)

    with open(LAST_RUN_LAST_RUN_FILE_PATH, "w") as f:
        f.write(current_time.strftime("%Y-%m-%d %H:%M:%S"))


def download_and_extract_data():
    """
    Downloads and extracts the data from the given url to the target directory.

    :return: None
    :rtype: None
    """
    from config import GSOY_DATA_DIR
    os.makedirs(GSOY_DATA_DIR, exist_ok=True)

    file_name = os.path.join(GSOY_DATA_DIR, 'gsoy-latest.tar.gz')
    urllib.request.urlretrieve(GSOY_DOWNLOAD_URL, file_name)

    tar = tarfile.open(file_name, 'r:gz')
    tar.extractall(GSOY_DATA_DIR)
    tar.close()

    os.remove(file_name)
