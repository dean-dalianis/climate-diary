from datetime import datetime, timedelta, timezone

from analysis import drop_analysis_data, analyze_data_and_write_to_db
from config import DATATYPE_ID, MIN_START_YEAR, MEASUREMENT_NAMES
from influx import fetch_gsom_data_from_db, wait_for_db, fetch_latest_timestamp
from logging_config import logger
from noaa_requests import make_api_request
from util import datetime_to_string, string_to_datetime, update_last_run, should_run, get_country_alpha_2

MAX_STATIONS = 5000  # The maximum number of stations to fetch data for -- used for fetching data faster for testing purposes

empty_station_details = {
    'elevation': float('inf'),
    'latitude': float('inf'),
    'longitude': float('inf'),
    'name': 'N/A'
}


def fetch_countries():
    """
    Fetch and return a list of all countries.

    :return: A list of countries.
    :rtype: list or None
    """
    logger.info(f'Fetching countries...')
    countries_url = f"locations?datasetid=GSOM&locationcategoryid=CNTRY&limit=1000"
    countries, ignored, ignored = make_api_request(countries_url)
    if len(countries) == 0:
        logger.error('Failed to fetch countries')
        exit(1)

    logger.info(f'Fetched {len(countries)} countries.')

    return [country for country in countries]


def fetch_stations(country_id, start_date):
    """
    Fetches and returns a map of all stations for a given country.

    :param dict country_id: The country_id to fetch the stations for.
    :param datetime start_date: The start of the date range.
    :return: A map of all stations for the given country with the station ID as the key and the station details as the value.
    :rtype: dict or None
    """
    start_date_str = datetime_to_string(start_date)
    stations_url = f"stations?datasetid=GSOM&&units=metric&locationid={country_id}&startdate={start_date_str}&limit=1000"
    stations, ignored, ignored = make_api_request(stations_url)

    logger.info(f'Fetching stations for {country_id}...')

    station_map = {}
    for station in stations:
        station_map[station['id']] = {}
        for field in ['elevation', 'latitude', 'longitude']:
            if field in station:
                station_map[station['id']][field] = float(station[field])
            else:
                station_map[station['id']][field] = None
        station_map[station['id']]['name'] = station.get('name', None)

    if len(stations) == 0:
        logger.error('Failed to fetch stations')
        return None

    logger.info(f'Fetched {len(station_map)} stations for {country_id}...')

    return station_map


def fetch_gsom_data(country_id, start_date, end_date, offset):
    """
    Fetch and return climate data for the specified country and date range.

    :param str country_id: The ID of the country to fetch data for.
    :param datetime start_date: The start of the date range.
    :param datetime end_date: The end of the date range.
    :return: A list of climate data for the specified country and date range, and a boolean indicating if there is more data.
    :rtype: list or None, bool
    """
    start_date_str = datetime_to_string(start_date)
    end_date_str = datetime_to_string(end_date)
    data_url = f"data?datasetid=GSOM&datatypeid={DATATYPE_ID}&units=metric&locationid={country_id}&startdate={start_date_str}&enddate={end_date_str}&limit=1000"
    data, has_more_data, offset = make_api_request(data_url, offset)
    if data is None:
        logger.error(f'Failed to fetch climate data for country {country_id} from {start_date_str} to {end_date_str}')
    return data, has_more_data, offset


def init_dates(country):
    found_previous_data = False
    latest_timestamp = fetch_latest_timestamp(country)
    if latest_timestamp is not None:
        logger.info(f'Found previous timestamp for {country["name"]}: {latest_timestamp}')
        latest_timestamp = latest_timestamp + timedelta(days=1)
        found_previous_data = True
    else:
        latest_timestamp = datetime(MIN_START_YEAR, 1, 1, tzinfo=timezone.utc)
    earliest_timestamp = string_to_datetime(country['mindate']).replace(tzinfo=timezone.utc)
    start_date = max(earliest_timestamp, latest_timestamp)
    end_date = string_to_datetime(country['maxdate']).replace(tzinfo=timezone.utc)
    return end_date, start_date, found_previous_data


def calculate_current_end_date(end_date, start_date):
    """
    Calculate the end date for the current 10 years taking into account leap years.

    :param datetime end_date: The end date of the date range.
    :param datetime start_date: The start date of the date range.
    :return: The end date for the current 10 years.
    :rtype: datetime
    """
    current_end_date = start_date + timedelta(days=3652)  # 10 years * 365 days + 2 extra for potential leap years
    current_end_date = min(current_end_date, end_date)
    return current_end_date


def create_fields_map(country, record, station_details):
    """
    Create a map of fields for a climate data record.

    :param dict country: The country information.
    :param dict record: The current climate data record.
    :param dict station_details: The details of the station associated with the record.
    :return: A map of fields for the climate data record.
    :rtype: dict
    """
    fields = {
        'value': float(record['value']) if 'value' in record else None,
        'country_name': country['name'],
        'station': record['station'] if 'station' in record else None,
        'station_name': station_details['name'],
        'latitude': station_details['latitude'],
        'longitude': station_details['longitude'],
        'elevation': station_details['elevation']
    }
    return fields


def create_points_dict(country, fields, record):
    """
    Create a dictionary representing a data point for writing to DB.

    Data includes:
    - measurement: The name of the measurement. e.g. TMAX
    - tags: country_id
    - time: The date of the data point.
    - fields: The map of fields for the data point:
        - value
        - country_name
        - station
        - latitude
        - longitude
        - elevation

    :param dict country: The country information.
    :param dict fields: The map of fields for the data point.
    :param dict record: The current climate data record.
    :return: A dictionary representing a data point for DB.
    :rtype: dict
    """
    return {
        'measurement': MEASUREMENT_NAMES.get(record['datatype']),
        'tags': {
            'country_id': get_country_alpha_2(country['name'])
        },
        'time': string_to_datetime(record['date']),
        'fields': {
            **fields,
        }
    }


def analyze_data(country):
    """
    Analyzes the data for a country.

    :param dict country: The country to analyze.
    :return: None
    """
    logger.info(f'Starting analysis for {country["name"]}')
    drop_analysis_data(country)
    for datatype in MEASUREMENT_NAMES.keys():
        data = fetch_gsom_data_from_db(country, MEASUREMENT_NAMES[datatype])
        if len(data) == 0:
            continue
        analyze_data_and_write_to_db(country, datatype, data)
    logger.info(f'Analysis finished for {country["name"]}')


def fetch_gsom_data_from_noaa_and_write_to_database(countries):
    """
    Fetches climate data from NOAA and writes it to the database.

    :return: None
    :rtype: None
    """
    while len(countries) > 0:
        new_data = False
        country = countries.pop()
        if get_country_alpha_2(country['name']) is None:
            continue

        logger.info(f'Fetching climate data for country: {country["name"]}')

        end_date, start_date, found_previous_data = init_dates(country)

        if (end_date - start_date) < timedelta(days=27):
            logger.info(f'No new data to fetch for {country["name"]}: {start_date} - {end_date}')
            continue

        station_map = fetch_stations(country['id'], start_date)
        if station_map is not None and len(station_map) > MAX_STATIONS:
            logger.warning(f'Country {country["name"]} has more than {MAX_STATIONS} stations. Skipping for now...')
            continue

        while start_date <= end_date:
            current_end_date = calculate_current_end_date(end_date, start_date)

            # Initialize offset for pagination
            offset = 0
            while True:
                gsom_data, has_more_data, offset = fetch_gsom_data(country['id'], start_date, current_end_date, offset)

                if gsom_data is None:
                    break

                logger.info(f'Fetched climate data for {country["name"]}: {start_date} - {current_end_date}')

                points = []
                for record in gsom_data:
                    if station_map is not None:
                        station_details = station_map.get(record['station'], empty_station_details)
                    fields = create_fields_map(country, record, station_details)
                    if fields['value'] is None:
                        continue
                    points_dict = create_points_dict(country, fields, record)
                    points.append(points_dict)

                # Write data to DB here
                logger.info(f'Writing climate info for {country["name"]} to db')
                from influx import write_points_to_db
                write_points_to_db(points, country)
                new_data = True
                if not has_more_data:
                    break

            start_date = current_end_date + timedelta(days=1)
        if new_data:
            analyze_data(country)


def main():
    if should_run():
        wait_for_db()

        countries = fetch_countries() or []

        logger.info('Fetching climate data...')
        fetch_gsom_data_from_noaa_and_write_to_database(countries)
        logger.info('Fetching climate data finished.')

        update_last_run()


if __name__ == '__main__':
    main()
