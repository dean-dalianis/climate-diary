import concurrent.futures
from datetime import datetime, timedelta, timezone

from analysis import drop_analysis_data, analyze_data_and_write_to_db
from config import ATTRIBUTES, EXCLUDED_ATTRIBUTES, EU_CONTINENT_FIPS, DATATYPE_ID, MIN_START_YEAR, MEASUREMENT_NAMES, \
    MAX_WORKERS
from influx import fetch_gsom_data_from_db, wait_for_db, fetch_latest_timestamp
from logging_config import logger
from noaa_requests import make_api_request
from util import datetime_to_string, string_to_datetime, update_last_run, should_run

empty_station_details = {
    'elevation': float('inf'),
    'latitude': float('inf'),
    'longitude': float('inf'),
    'name': 'N/A'
}

COUNTRIES_TO_ANALYZE = []


def decode_attributes(datatype, attributes_str):
    """
    Decode the attributes string for a specified datatype.
    The attributes string is a comma separated string of values in the order specified in the config file.

    Attributes are decoded as follows:
        - days_missing: int
        - day: int (optional)
        - more_than_once: bool (optional)


    :param str datatype: The datatype of the attributes.
    :param str attributes_str: The attributes string to decode.
    :return: The decoded attributes.
    :rtype: dict
    """
    attribute_names = ATTRIBUTES.get(datatype, [])
    attributes = attributes_str.split(',')

    decoded_attributes = {}
    for i, name in enumerate(attribute_names):
        # Check if the attribute value exists, else provide default.
        if i < len(attributes):
            if name == 'days_missing' or name == 'day':
                value = int(attributes[i]) if attributes[i] != '' else 0
            elif name == 'more_than_once':
                value = True if attributes[i] == '+' else False
            else:
                value = attributes[i]
        else:
            if name == 'days_missing' or name == 'day':
                value = 0
            elif name == 'more_than_once':
                value = False
            else:
                value = ''

        # Add attribute to the decoded attributes dictionary if it's not excluded
        if name not in EXCLUDED_ATTRIBUTES:
            decoded_attributes[name] = value

    return decoded_attributes


def fetch_countries():
    """
    Fetch and return a list of all countries.

    :return: A list of countries.
    :rtype: list or None
    """
    logger.info(f'Fetching countries...')
    countries_url = f"locations?datasetid=GSOM&locationcategoryid=CNTRY&limit=1000"
    countries = make_api_request(countries_url)
    if len(countries) == 0:
        logger.error('Failed to fetch countries')
        exit(1)

    logger.info(f'Fetched {len(countries)} countries.')

    return [country for country in countries if not country['id'].split(':')[1] in EU_CONTINENT_FIPS]


def fetch_european_countries():
    """
     Fetch and return a list of European countries.

     This function fetches the list of all countries and filters it to include only the European countries.
     The filtering is based on the continent code of each country. Only the countries with a continent code
     present in the EU_CONTINENT_FIPS list are considered as European countries.

     :return: A list of European countries.
     :rtype: list or None
     """
    all_countries = fetch_countries()
    european_countries = [country for country in all_countries if country['id'].split(':')[1] in EU_CONTINENT_FIPS]
    if len(european_countries) == 0:
        logger.error('Failed to fetch European countries')
        exit(1)
    logger.info(f'Fetched {len(european_countries)} European countries.')
    return european_countries


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
    stations = make_api_request(stations_url)

    logger.info(f'Fetching stations for {country_id}...')

    station_map = {}
    for station in stations:
        station_map[station['id']] = {
            'elevation': station.get('elevation', float('inf')),
            'latitude': station.get('latitude', float('inf')),
            'longitude': station.get('longitude', float('inf')),
            'name': station.get('name', 'N/A')
        }

    if len(stations) == 0:
        logger.error('Failed to fetch stations')
        return None

    logger.info(f'Fetched {len(station_map)} stations for {country_id}...')

    return station_map


def fetch_gsom_data(country_id, start_date, end_date):
    """
    Fetch and return climate data for the specified country and date range.

    :param str country_id: The ID of the country to fetch data for.
    :param datetime start_date: The start of the date range.
    :param datetime end_date: The end of the date range.
    :return: A list of climate data for the specified country and date range.
    :rtype: list or None
    """
    start_date_str = datetime_to_string(start_date)
    end_date_str = datetime_to_string(end_date)
    data_url = f"data?datasetid=GSOM&datatypeid={DATATYPE_ID}&units=metric&locationid={country_id}&startdate={start_date_str}&enddate={end_date_str}&limit=1000"
    data = make_api_request(data_url)
    if data is None:
        logger.error(f'Failed to fetch climate data for country {country_id} from {start_date_str} to {end_date_str}')
    return data


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
        'value': float(record['value']),
        'country_name': country['name'],
        'station': record['station'],
        'latitude': float(station_details['latitude']),
        'longitude': float(station_details['longitude']),
        'elevation': float(station_details['elevation'])
    }
    if 'attributes' in record:
        fields.update(decode_attributes(record['datatype'], record['attributes']))
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
        - other attributes

    :param dict country: The country information.
    :param dict fields: The map of fields for the data point.
    :param dict record: The current climate data record.
    :return: A dictionary representing a data point for DB.
    :rtype: dict
    """
    return {
        'measurement': MEASUREMENT_NAMES.get(record['datatype']),
        'tags': {
            'country_id': country['id'].split(':')[1]
        },
        'time': string_to_datetime(record['date']),
        'fields': {
            **fields,
        }
    }


def fetch_measurements_from_db(country):
    """
    Fetches all measurements from DB for a country.

    :param dict country: The country for which to fetch measurements.
    :return: A map of measurements. Each key is the name of the measurement, and its value is a list of tuples containing the date and value of the measurement.
    :rtype: dict
    """
    data_for_analysis = {datatype: [] for datatype in MEASUREMENT_NAMES.keys()}

    for datatype in MEASUREMENT_NAMES.keys():
        db_data = fetch_gsom_data_from_db(country, MEASUREMENT_NAMES[datatype])
        if db_data is not None:
            for record in db_data:
                data_for_analysis[datatype].append((record['date'], record['value']))
        logger.info(
            f'Fetched {len(data_for_analysis[datatype])} points to analyze for {MEASUREMENT_NAMES[datatype]}')

    return data_for_analysis


def fetch_gsom_data_from_noaa_and_write_to_database():
    """
    Fetches climate data from NOAA and writes it to the database.

    :return: None
    :rtype: None
    """
    countries = fetch_countries() or []

    for country in countries:
        points = []
        logger.info(f'Fetching climate data for country: {country["name"]}')

        end_date, start_date, found_previous_data = init_dates(country)

        wrote_new_data = False

        station_map = fetch_stations(country['id'], start_date)

        while start_date <= end_date:
            current_end_date = calculate_current_end_date(end_date, start_date)
            if (gsom_data := fetch_gsom_data(country['id'], start_date, current_end_date)) is not None:
                logger.info(f'Fetched climate data for {country["name"]}: {start_date} - {current_end_date}')

                wrote_new_data = True

                for record in gsom_data:
                    station_details = station_map.get(record['station'], empty_station_details)
                    fields = create_fields_map(country, record, station_details)
                    points_dict = create_points_dict(country, fields, record)
                    points.append(points_dict)

            start_date = current_end_date + timedelta(days=1)

        if points:
            logger.info(f'Writing climate info for {country["name"]} to db')

            from influx import write_points_to_db
            write_points_to_db(points, country)

            if wrote_new_data:
                COUNTRIES_TO_ANALYZE.append(country)
        else:
            logger.warning('No data to write. Maybe everything is already there?')


def analyze_countries():
    """
    Analyzes the data for each country in COUNTRIES_TO_ANALYZE using multiple threads.

    :return: None
    :rtype: None
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(analyze_data, COUNTRIES_TO_ANALYZE)


def analyze_data(country):
    """
    Analyzes the data for a country.

    :param dict country: The country to analyze.
    :return: None
    """
    logger.info(f'Starting analysis for {country["name"]}')
    drop_analysis_data(country)
    data_for_analysis = fetch_measurements_from_db(country)
    logger.info(f'Fetched {len(data_for_analysis)} measurements for {country["name"]}')
    analyze_data_and_write_to_db(country, data_for_analysis)
    logger.info(f'Analysis finished for {country["name"]}')


def main():
    if should_run():
        wait_for_db()

        logger.info('Fetching climate data...')
        fetch_gsom_data_from_noaa_and_write_to_database()
        logger.info('Fetching climate data finished.')

        logger.info('Analyzing countries with new data...')
        analyze_countries()
        logger.info('Analysis finished.')

        update_last_run()


if __name__ == '__main__':
    main()
