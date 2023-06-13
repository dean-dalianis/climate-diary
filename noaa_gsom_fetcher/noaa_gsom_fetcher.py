import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import numpy as np
from dateutil.parser import parse

from influx import write_points_to_influx, wait_for_influx, fetch_latest_timestamp_for_average_temperature, \
    fetch_climate_data_from_influx, drop_trend
from logging_config import logger
from noaa_requests import make_api_request
from util import datetime_to_string, string_to_datetime

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config/config.json')
with open(CONFIG_FILE, 'r') as file:
    config = json.load(file)

MIN_START_YEAR = config["MIN_START_YEAR"]
DATATYPE_ID = config["DATATYPE_ID"]
EU_CONTINENT_FIPS = config["EU_CONTINENT_FIPS"]
ATTRIBUTES = config["ATTRIBUTES"]
MEASUREMENT_NAMES = config["MEASUREMENT_NAMES"]

empty_station_details = {
    'elevation': float('inf'),
    'latitude': float('inf'),
    'longitude': float('inf'),
    'name': 'N/A'
}

EXCLUDED_ATTRIBUTES = ['source_code', 'daily_dataset_measurement_source_code', 'daily_dataset_flag', 'measurement_flag',
                       'quality_flag']


def decode_attributes(datatype, attributes_str):
    """
    Decode the attributes string for a given datatype and return as a dictionary.

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

    return countries


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
    :return: A map of stations. Each key is the id of the station, and its value is a dictionary containing the 'elevation', 'latitude', 'longitude', and 'name' of the station.
    :rtype: dict
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


def fetch_climate_data(country_id, start_date, end_date):
    """
    Fetch and return climate data for the specified country and date range.

    :param str country_id: The ID of the country to fetch data for.
    :param datetime start_date: The start of the date range.
    :param datetime end_date: The end of the date range.
    :return: Climate data for the specified country and date range.
    :rtype: list or None
    """
    start_date_str = datetime_to_string(start_date)
    end_date_str = datetime_to_string(end_date)
    data_url = f"data?datasetid=GSOM&datatypeid={DATATYPE_ID}&units=metric&locationid={country_id}&startdate={start_date_str}&enddate={end_date_str}&limit=1000"
    data = make_api_request(data_url)
    if data is None:
        logger.error(f'Failed to fetch climate data for country {country_id} from {start_date_str} to {end_date_str}')
    return data


def calculate_avg_temp_decadal_averages(data):
    """
    This function calculates the average temperature for each decade in the given dataset. It first groups the temperature data by decade, then computes the average temperature for each decade.

    :param list data: The data from which to calculate averages, each element is a dictionary containing a 'date' and 'value'.
    :return: A dictionary where keys are decades (e.g., 1990, 2000) and values are the respective average temperature.
    :rtype: dict
    """
    decadal_data = {}
    for record in data:
        decade = (parse(record['date']).year // 10) * 10
        if decade not in decadal_data:
            decadal_data[decade] = []
        decadal_data[decade].append(record['value'])

    decadal_averages = {decade: sum(values) / len(values) for decade, values in decadal_data.items()}

    return decadal_averages


def calculate_trends_and_write_to_influx(country, data_for_trend):
    """
    This function calculates the trend (linear regression) for each data type (e.g., average temperature) and writes this trend data to InfluxDB.
    It uses numpy's polyfit method to calculate the slope and intercept of the trend line. If there's no data available for a certain datatype for the given country, it logs a warning.

    :param dict country: The country for which to calculate trends.
    :param dict data_for_trend: A dictionary where the key is the datatype, and the value is a list of tuples, each containing a timestamp and a value.
    """
    for datatype, data in data_for_trend.items():
        if data:
            timestamps, values = zip(*data)
            timestamps = [mdates.date2num(ts) for ts in timestamps]
            trend_slope, trend_intercept = np.polynomial.polynomial.polyfit(timestamps, values, 1)
            trend_point = {
                'measurement': f'{MEASUREMENT_NAMES[datatype]}_trend',
                'tags': {
                    'country': country['name']
                },
                'fields': {
                    'slope': trend_slope,
                    'intercept': trend_intercept,
                }
            }
            logger.info(f'Writing data trend for {datatype} for {country["name"]} to db')
            write_points_to_influx([trend_point], country)
        else:
            logger.warn(f'No data for trend calculation for {datatype} for {country["name"]}')


def init_dates(country):
    """
    Initialize start and end dates for fetching climate data based on the country's information.

    :param dict country: The country for which to initialize dates.
    :return: The end date, start date, and a flag if it finds previous written data.
    """
    found_previous_data = False
    latest_timestamp = fetch_latest_timestamp_for_average_temperature(country)
    if latest_timestamp is not None:
        latest_timestamp = latest_timestamp + timedelta(days=1)
        found_previous_data = True
    else:
        latest_timestamp = datetime(MIN_START_YEAR, 1, 1, tzinfo=ZoneInfo("UTC"))
    start_date = max(
        string_to_datetime(country['mindate']),
        datetime(MIN_START_YEAR, 1, 1, tzinfo=ZoneInfo("UTC")),
        latest_timestamp
    )
    end_date = string_to_datetime(country['maxdate'])
    return end_date, start_date, found_previous_data


def calculate_yoy_and_dod_change(decade, prev_decade_values, prev_year_values, record, year):
    """
    Calculate year-over-year (YoY) and decade-over-decade (DoD) changes in temperature based on previous values.

    :param int decade: The decade of the current record.
    :param dict prev_decade_values: Dictionary containing previous decade values.
    :param dict prev_year_values: Dictionary containing previous year values.
    :param dict record: The current climate data record.
    :param int year: The year of the current record.
    :return: The DoD and YoY changes in temperature.
    :rtype: tuple
    """
    if year - 1 in prev_year_values:
        yoy_change = float(record['value']) - prev_year_values[year - 1]
    else:
        yoy_change = None
    if decade - 10 in prev_decade_values:
        dod_change = float(record['value']) - prev_decade_values[decade - 10]
    else:
        dod_change = None
    return dod_change, yoy_change


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
        'country_id': country['id'].split(':')[1],
        'station': record['station'],
        'latitude': float(station_details['latitude']),
        'longitude': float(station_details['longitude']),
        'elevation': float(station_details['elevation'])
    }
    if 'attributes' in record:
        fields.update(decode_attributes(record['datatype'], record['attributes']))
    return fields


def create_points_dict(avg_temp_decadal_averages, country, decade, dod_change, fields, record, yoy_change):
    """
    Create a dictionary representing a data point for writing to InfluxDB.

    :param dict avg_temp_decadal_averages: Decadal average temperatures.
    :param dict country: The country information.
    :param int decade: The decade associated with the data point.
    :param float dod_change: Day-over-day temperature change.
    :param dict fields: The map of fields for the data point.
    :param dict record: The current climate data record.
    :param float yoy_change: Year-over-year temperature change.
    :return: A dictionary representing a data point for InfluxDB.
    :rtype: dict
    """
    return {
        'measurement': MEASUREMENT_NAMES.get(record['datatype']),
        'tags': {
            'country': country['name']
        },
        'time': string_to_datetime(record['date']),
        'fields': {
            **fields,
            'yoy_change': yoy_change,
            'dod_change': dod_change,
            'decadal_average_temperature': avg_temp_decadal_averages[decade]
            if record['datatype'] == 'TAVG' else None
        }
    }


def fetch_and_write_climate_data_to_influxdb():
    """
    Fetches climate data for each country, calculates temperature changes, creates data points, and writes them to InfluxDB.
    """
    countries = fetch_european_countries() or []

    for country in countries:
        points = []
        logger.info(f'Fetching climate data for country: {country["name"]}')

        end_date, start_date, found_previous_data = init_dates(country)

        wrote_new_data = False

        station_map = fetch_stations(country['id'], start_date)

        data_for_trend = {datatype: [] for datatype in MEASUREMENT_NAMES.keys()}
        prev_year_values = {}
        prev_decade_values = {}

        while start_date <= end_date:
            current_end_date = min(start_date + timedelta(days=9 * 365), end_date)
            if (climate_data := fetch_climate_data(country['id'], start_date, current_end_date)) is not None:
                logger.info(f'Fetched climate data for {country["name"]}: {start_date} - {current_end_date}')

                wrote_new_data = True

                avg_temp_data = [record for record in climate_data if record['datatype'] == 'TAVG']
                avg_temp_decadal_averages = calculate_avg_temp_decadal_averages(avg_temp_data)

                for record in climate_data:
                    station_details = station_map.get(record['station'], empty_station_details)
                    fields = create_fields_map(country, record, station_details)

                    year = string_to_datetime(record['date']).year
                    decade = (year // 10) * 10

                    dod_change, yoy_change = calculate_yoy_and_dod_change(decade, prev_decade_values, prev_year_values,
                                                                          record, year)

                    prev_year_values[year] = float(record['value'])
                    prev_decade_values[decade] = float(record['value'])

                    points_dict = create_points_dict(avg_temp_decadal_averages, country, decade, dod_change, fields,
                                                     record, yoy_change)
                    points.append(points_dict)

                    if not found_previous_data:
                        data_for_trend[record['datatype']].append(
                            (string_to_datetime(record['date']), float(record['value'])))

            start_date = current_end_date + timedelta(days=1)

        if points:
            logger.info(f'Writing climate info for {country} to db')
            write_points_to_influx(points, country)
            if wrote_new_data:
                logger.info('Fetching data from influx to recalculate trend lines')
                for datatype in MEASUREMENT_NAMES.keys:
                    drop_trend(country['name'], f'{MEASUREMENT_NAMES[datatype]}_trend')
                for datatype in MEASUREMENT_NAMES.keys():
                    influx_data = fetch_climate_data_from_influx(country, MEASUREMENT_NAMES[datatype])
                    if influx_data is not None:
                        for record in influx_data:
                            data_for_trend[datatype].append((record['date'], record['value']))
                    logger.info(
                        f'Fetched {len(data_for_trend[datatype])} points to calculate trend lines for {MEASUREMENT_NAMES[datatype]}')
        else:
            logger.warn('No data to write. Maybe everything is already there?')

        calculate_trends_and_write_to_influx(country, data_for_trend)


if __name__ == "__main__":
    wait_for_influx()
    fetch_and_write_climate_data_to_influxdb()
    logger.info('Fetching climate data finished')
