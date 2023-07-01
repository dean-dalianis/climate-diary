import os
import shutil
import tarfile
import urllib.request
from datetime import datetime, timedelta, timezone


def should_run():
    """
     Determines if 15 days have passed since the last run.

     :return: Whether the script should run.
     :rtype: bool
     """
    from logging_config import logger
    from config import LAST_RUN_LAST_RUN_FILE_PATH

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

    from influx import write_points_to_db
    from config import LAST_RUN_LAST_RUN_FILE_PATH

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

    write_points_to_db(last_run_point)

    os.makedirs(os.path.dirname(LAST_RUN_LAST_RUN_FILE_PATH), exist_ok=True)

    with open(LAST_RUN_LAST_RUN_FILE_PATH, "w") as f:
        f.write(current_time.strftime("%Y-%m-%d %H:%M:%S"))


def extract_tar_file(file_name):
    """
    Extracts the tar file to the 'extracted_data' directory within the target directory.

    :param file_name: Name of the tar file to extract.
    :type file_name: str
    :return: None
    :rtype: None
    """
    from config import GSOY_DATA_DIR
    from logging_config import logger

    extracted_data_dir = os.path.join(GSOY_DATA_DIR, 'extracted_data')
    os.makedirs(extracted_data_dir, exist_ok=True)

    tar = tarfile.open(file_name, 'r:gz')
    logger.info('Extracting tar file...')
    tar.extractall(extracted_data_dir)
    tar.close()
    logger.info('Tar file extracted successfully.')


def download_and_extract_data():
    """
    Downloads and extracts the data from the given URL to the target directory.
    If the tar file already exists and was downloaded within the last 29 days, it will be extracted without re-downloading.

    :return: None
    :rtype: None
    """
    from config import GSOY_DATA_DIR
    from logging_config import logger
    from config import GSOY_DOWNLOAD_URL

    os.makedirs(GSOY_DATA_DIR, exist_ok=True)

    file_name = os.path.join(GSOY_DATA_DIR, 'gsoy-latest.tar.gz')

    if os.path.exists(file_name):
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_name))
        current_time = datetime.now()
        time_diff = current_time - modified_time

        if time_diff <= timedelta(days=15):
            logger.info('The tar file already exists and was downloaded within the last 15 days. Skipping download.')
            if os.path.exists(os.path.join(GSOY_DATA_DIR, 'extracted_data')):
                logger.info('Extracted data already exists. Skipping extraction.')
            else:
                extract_tar_file(file_name)
            return
        else:
            logger.info('The tar file already exists but was downloaded more than 15 days ago. Downloading again.')
            os.remove(file_name)

    logger.info('Downloading tar file...')
    urllib.request.urlretrieve(GSOY_DOWNLOAD_URL, file_name)
    logger.info('Tar file downloaded successfully.')

    extract_tar_file(file_name)


def remove_extracted_data():
    """
    Removes the previously extracted data directory from the target directory.

    :return: None
    :rtype: None
    """
    from config import GSOY_DATA_DIR
    from logging_config import logger

    extracted_data_dir = os.path.join(GSOY_DATA_DIR, 'extracted_data')

    if os.path.exists(extracted_data_dir):
        shutil.rmtree(extracted_data_dir)
        logger.info('Extracted data removed successfully.')
    else:
        logger.info('No extracted data found.')
