import concurrent.futures
import csv
import os

from config import FIELD_MAPPING, GSOY_DATA_DIR, FIPS_MAPPING
from influx import write_points_to_db
from logging_config import logger
from util import update_last_run, download_and_extract_data, remove_extracted_data

MAX_WORKERS = 4


def import_file(filename):
    logger.info(f'Importing data from {filename}')
    if filename.endswith('.csv'):
        file_path = os.path.join(GSOY_DATA_DIR, "extracted_data", filename)
        country_fips_code = filename[:2]

        if country_fips_code not in FIPS_MAPPING.keys():
            logger.error(f'No country found for "FIPS:{country_fips_code}"')
            return

        # country_name = FIPS_MAPPING[country_fips_code].get('country_name', None)
        country_iso = FIPS_MAPPING[country_fips_code].get('country_iso', None)

        with open(file_path, 'r') as file:
            points = []
            csv_reader = csv.reader(file)
            headers = next(csv_reader)

            for row in csv_reader:
                # station = row[0]
                time = f'{row[1]}-01-01T00:00:00.000Z'
                # latitude = row[2]
                # longitude = row[3]
                # elevation = row[4]
                # station_name = row[5]

                for i, field_value in enumerate(row):
                    field_name = headers[i]
                    if field_name not in FIELD_MAPPING:
                        # Filter out fields that are not in the mapping
                        continue

                    human_readable_name = FIELD_MAPPING.get(field_name, {}).get('name', field_name)
                    value = row[headers.index(field_name)]
                    if value == '':
                        continue
                    fields = {
                        'value': float(row[headers.index(field_name)]),
                        # 'station': station,
                        # 'latitude': latitude,
                        # 'longitude': longitude,
                        # 'elevation': elevation,
                        # 'station_name': station_name,
                        # 'country_name': country_name
                    }

                    data = {
                        'measurement': human_readable_name,
                        'tags': {
                            'country_iso': country_iso,
                        },
                        'time': time,
                        'fields': fields
                    }

                    points.append(data)
    write_points_to_db(points)


def import_data():
    logger.info('Starting download...')
    download_and_extract_data()
    logger.info('Download and extraction complete.')

    extracted_data_dir = os.path.join(GSOY_DATA_DIR, 'extracted_data')
    filenames = os.listdir(extracted_data_dir)
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(import_file, filenames)

    update_last_run()


if __name__ == '__main__':
    logger.info('Starting import')
    import_data()
    logger.info('Import finished')
    logger.info('Removing extracted data')
    remove_extracted_data()
    logger.info('Removed extracted data')
