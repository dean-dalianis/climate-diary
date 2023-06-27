import csv
import os

from analysis import analyze_data_and_write_to_db
from config import FIELD_MAPPING, GSOY_DATA_DIR, FIPS_MAPPING
from influx import write_points_to_db, fetch_gsom_data_from_db
from logging_config import logger
from util import update_last_run, download_and_extract_data


def import_data():
    download_and_extract_data()
    for filename in os.listdir(GSOY_DATA_DIR):
        if filename.endswith('.csv'):
            file_path = os.path.join(GSOY_DATA_DIR, filename)
            country_name = FIPS_MAPPING[filename[:2]].get('country_name', None)
            country_iso = FIPS_MAPPING[filename[:2]].get('country_iso', None)

            if country_name is None or country_iso is None:
                logger.error(f'No country found for "FIPS:{filename[:2]}"')
                continue

            with open(file_path, 'r') as file:
                points = []
                csv_reader = csv.reader(file)
                headers = next(csv_reader)

                for row in csv_reader:
                    station = row[0]
                    time = row[1]
                    latitude = row[2]
                    longitude = row[3]
                    elevation = row[4]
                    station_name = row[5]

                    for i, field_value in enumerate(row):
                        field_name = headers[i]
                        if field_name not in FIELD_MAPPING.keys():
                            continue
                        human_readable_name = FIELD_MAPPING.get(field_name, {}).get('name', field_name)
                        value = row[headers.index(field_name)]
                        if value == '':
                            continue
                        fields = {
                            'value': float(row[headers.index(field_name)]),
                            'station': station,
                            'latitude': latitude,
                            'longitude': longitude,
                            'elevation': elevation,
                            'station_name': station_name,
                            'country_name': country_name
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
    update_last_run()


def analyze(country_iso):
    """
    Analyzes the data for a country.

    :param country_iso: The country to analyze.
    :return: None
    """
    for measurement in FIELD_MAPPING:
        measurement_name = FIELD_MAPPING[measurement].get('name')
        data = fetch_gsom_data_from_db(country_iso, measurement_name)
        if data is None or len(data) == 0:
            continue
        logger.debug(f'Found {len(data)} data points for analysis for {measurement_name} in {country_iso}')
        analyze_data_and_write_to_db(country_iso, measurement_name, data)


def analyze_data():
    """
    Analyzes the data for all countries.

    :return: None
    """
    logger.info('Starting analysis')
    for country in FIPS_MAPPING:
        logger.info(f'Analyzing data for {country["country_name"]}')
        country_iso = FIPS_MAPPING[country].get('country_iso')
        analyze(country_iso)
        logger.info('Analysis finished for {country["country_name"]}')
    logger.info('Analysis finished')


if __name__ == '__main__':
    logger.info('Starting import')
    import_data()
    logger.info('Import finished')
