import json
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
from dateutil.parser import parse

from influx import write_points_to_influx, wait_for_influx, fetch_latest_timestamp_for_average_temperature
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

    # Fill missing attributes with default values
    while len(attributes) < len(attribute_names):
        if attribute_names[len(attributes)] == 'days_missing':
            attributes.append('0')
        else:
            attributes.append('')

    return {
        name: attributes[i]
        for i, name in enumerate(attribute_names)
        if name != 'source_code'
    }


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


def calculate_decadal_averages(data):
    # Group data by decade
    decadal_data = {}
    for record in data:
        # Here we assume that the 'date' field in record is a datetime object
        decade = (record['date'].year // 10) * 10
        if decade not in decadal_data:
            decadal_data[decade] = []
        decadal_data[decade].append(record['value'])

    # Calculate averages
    decadal_averages = {decade: sum(values) / len(values) for decade, values in decadal_data.items()}

    return decadal_averages


def fetch_and_write_climate_data_to_influxdb():
    """
    Fetches climate data for each country and writes them to the influx.
    """
    countries = fetch_european_countries() or []

    for country in countries:
        points = []
        logger.info(f'Fetching climate data for country: {country["name"]}')

        latest_timestamp = fetch_latest_timestamp_for_average_temperature(country)
        if latest_timestamp is not None:
            latest_timestamp = latest_timestamp + timedelta(days=1)
        else:
            latest_timestamp = datetime(MIN_START_YEAR, 1, 1, tzinfo=ZoneInfo("UTC"))

        start_date = max(
            string_to_datetime(country['mindate']),
            datetime(MIN_START_YEAR, 1, 1, tzinfo=ZoneInfo("UTC")),
            latest_timestamp
        )

        end_date = string_to_datetime(country['maxdate'])

        station_map = fetch_stations(country['id'], start_date)

        data_for_trend = {datatype: [] for datatype in MEASUREMENT_NAMES.keys()}

        while start_date <= end_date:
            current_end_date = min(start_date + timedelta(days=9 * 365), end_date)
            if (climate_data := fetch_climate_data(country['id'], start_date, current_end_date)) is not None:
                logger.info(f'Fetched climate data for {country}: {start_date} - {current_end_date}')

                avg_temp_data = [record for record in climate_data if record['datatype'] == 'TAVG']
                decadal_averages = calculate_decadal_averages(avg_temp_data)

                for record in climate_data:
                    station_details = station_map.get(record['station'], empty_station_details)
                    fields = {
                        "value": float(record['value']),
                        "country_id": country['id'].split(':')[1],
                        "station": record['station'],
                        "latitude": float(station_details['latitude']),
                        "longitude": float(station_details['longitude']),
                        "elevation": float(station_details['elevation'])
                    }

                    if 'attributes' in record:
                        fields.update(decode_attributes(record['datatype'], record['attributes']))

                    decade = (parse(record['date']).year // 10) * 10
                    points.append({
                        "measurement": MEASUREMENT_NAMES.get(record['datatype']),
                        "tags": {
                            "country": country['name']
                        },
                        "time": parse(record['date']).astimezone(timezone.utc).isoformat(),
                        "fields": {
                            **fields,
                            "decadal_average_temperature": decadal_averages[decade]
                            if record['datatype'] == 'TAVG' else None
                        }
                    })

                    data_for_trend[record['datatype']].append(
                        (parse(record['date']).timestamp(), float(record['value'])))

            start_date = current_end_date + timedelta(days=1)

        if points:
            write_points_to_influx(points, country)
        else:
            logger.error('No data to write')

        for datatype, data in data_for_trend.items():
            if data:
                timestamps, values = zip(*data)
                trend_slope, trend_intercept = np.polyfit(timestamps, values, 1)

                trend_point = {
                    "measurement": f"{MEASUREMENT_NAMES[datatype]}_trend",
                    "tags": {
                        "country": country['name']
                    },
                    "fields": {
                        "slope": trend_slope,
                        "intercept": trend_intercept,
                    }
                }
                write_points_to_influx([trend_point], country)
            else:
                logger.error(f'No data for trend calculation for {datatype}')


if __name__ == "__main__":
    wait_for_influx()
    fetch_and_write_climate_data_to_influxdb()
