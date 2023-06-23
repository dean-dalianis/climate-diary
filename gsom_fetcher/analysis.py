import numpy as np
from matplotlib.dates import date2num

from config import MEASUREMENT_NAMES
from influx import write_points_to_db, drop
from logging_config import logger


def analyze_data_and_write_to_db(country, datatype, data):
    """
    Analyze the data and write the results to the database.
    Analyzed data includes:
        - yearly averages
        - decadal averages
        - year-over-year changes
        - decade-over-decade changes
        - trends

    :param dict country: The country for which to calculate trends.
    :param str datatype: The measurement we're doing the analysis for
    :param list data: A list of dictionaries with data like [{'date': .., 'value':..}, {'date': .., 'value': ..}]
    :return: None
    :rtype: None
    """

    trend_points = calculate_trend_points(country, data, datatype)
    decadal_averages, yearly_averages = calculate_averages(data)
    dod_changes, yoy_changes = calculate_changes(data)

    write_points_to_db(trend_points, country)
    write_yearly_averages_to_db(country, yearly_averages, datatype)
    write_decadal_averages_to_db(country, decadal_averages, datatype)
    write_yoy_changes_to_db(country, yoy_changes, datatype)
    write_dod_changes_to_db(country, dod_changes, datatype)


def calculate_changes(data):
    """
    Calculates the year-over-year and decade-over-decade changes for the data.

    :param list data: A list of dictionaries with data like [{'date': .., 'value':..}, {'date': .., 'value': ..}]
    :return dict dod_changes: A dictionary containing the decade-over-decade changes.
    :return dict yoy_changes: A dictionary containing the year-over-year changes.
    :rtype: dict, dict
    """
    yoy_changes, dod_changes = {}, {}
    sorted_data = sorted(data, key=lambda d: d['date'])  # Sort data points by timestamp
    for i in range(1, len(sorted_data)):
        current_year = sorted_data[i]['date'].year
        prev_year = sorted_data[i - 1]['date'].year
        yoy_change = sorted_data[i]['value'] - sorted_data[i - 1]['value']
        yoy_changes.setdefault(current_year, []).append(yoy_change)
        if current_year != prev_year + 1:
            # Handle missing years in the data
            missing_years = range(prev_year + 1, current_year)
            for missing_year in missing_years:
                yoy_changes.setdefault(missing_year, []).append(None)

        current_decade = (sorted_data[i]['date'].year // 10) * 10
        prev_decade = (sorted_data[i - 1]['date'].year // 10) * 10
        dod_change = sorted_data[i]['value'] - sorted_data[i - 1]['value']
        dod_changes.setdefault(current_decade, []).append(dod_change)
        if current_decade != prev_decade + 10:
            # Handle missing decades in the data
            missing_decades = range(prev_decade + 10, current_decade, 10)
            for missing_decade in missing_decades:
                dod_changes.setdefault(missing_decade, []).append(None)
    return dod_changes, yoy_changes


def calculate_averages(data):
    """
    Calculates the yearly and decadal averages for the data.

    :param list data: A list of dictionaries with data like [{'date': .., 'value':..}, {'date': .., 'value': ..}]
    :return dict decadal_averages: A dictionary containing the decadal averages.
    :return dict yearly_averages: A dictionary containing the yearly averages.
    :rtype: dict, dict
    """
    yearly_averages, decadal_averages = {}, {}
    for d in data:
        timestamp, value = d['date'], d['value']
        year = timestamp.year
        decade = (year // 10) * 10

        yearly_averages.setdefault(year, []).append(value)
        decadal_averages.setdefault(decade, []).append(value)
    return decadal_averages, yearly_averages

def calculate_trend_points(country, data, measurement):
    from util import datetime_to_days_since_1880, datetime_to_string

    timestamps = [datetime_to_days_since_1880(d['date']) for d in data]
    values = [d['value'] for d in data]
    trend_slope, trend_intercept = np.polynomial.polynomial.polyfit(timestamps, values, 1)
    from util import get_country_alpha_2

    trend_points = []
    for i, timestamp in enumerate(timestamps):
        trend_point = {
            'measurement': f'{measurement}_trend',
            'time': datetime_to_string(data[i]['date']),  # convert the datetime object to string
            'fields': {
                'value': trend_slope * timestamp + trend_intercept,
                'country_name': country['name'],
                'country_id': get_country_alpha_2(country['name'])
            }
        }
        trend_points.append(trend_point)

    return trend_points



def write_monthly_averages_to_db(country, monthly_averages, datatype):
    """
    Writes the monthly averages to the DB for a specific country.

    :param dict country: The country information.
    :param dict monthly_averages: A dictionary containing the monthly averages.
    :param str datatype: The datatype for which to write the monthly averages.
    :return: None
    :rtype: None
    """
    from util import get_country_alpha_2

    points = []
    for year, months in monthly_averages.items():
        for month, values in months.items():
            metric = calculate_correct_metric(values, datatype)
            point = {
                'measurement': f'{MEASUREMENT_NAMES[datatype]}_monthly_average',
                'tags': {
                    'country_id': get_country_alpha_2(country['name']),
                },
                'time': f"{year}-{month:02d}-01T00:00:00Z",  # Setting time at the start of the month
                'fields': {
                    'value': metric,
                    'country_name': country['name']
                }
            }
            points.append(point)
    logger.info(f'Writing monthly averages for {country["name"]} to DB')
    write_points_to_db(points, country)


def write_yearly_averages_to_db(country, yearly_averages, datatype):
    """
    Writes the yearly averages to the DB for a specific country.

    :param dict country: The country information.
    :param dict yearly_averages: A dictionary containing the yearly averages.
    :param str datatype: The datatype for which to write the yearly averages.
    :return: None
    :rtype: None
    """
    from util import get_country_alpha_2

    points = []
    for year, values in yearly_averages.items():
        metric = calculate_correct_metric(values, datatype)
        point = {
            'measurement': f'{MEASUREMENT_NAMES[datatype]}_yearly_average',
            'tags': {
                'country_id': get_country_alpha_2(country['name'])
            },
            'time': f"{year}-01-01T00:00:00Z",  # Setting time at the start of the year
            'fields': {
                'value': metric,
                'country_name': country['name']
            }
        }
        points.append(point)
    logger.info(f'Writing yearly averages for {country["name"]} to DB')
    write_points_to_db(points, country)


def write_decadal_averages_to_db(country, decadal_averages, datatype):
    """
    Writes the decadal averages to the DB for a specific country.

    :param dict country: The country information.
    :param dict decadal_averages: A dictionary containing the decadal averages.
    :param str datatype: The datatype for which to write the decadal averages.
    :return: None
    :rtype: None
    """
    points = []
    for decade, values in decadal_averages.items():
        metric = calculate_correct_metric(values, datatype)
        from util import get_country_alpha_2
        point = {
            'measurement': f'{MEASUREMENT_NAMES[datatype]}_decadal_average',
            'tags': {
                'country_id': get_country_alpha_2(country['name']),
            },
            'time': f"{decade}-01-01T00:00:00Z",  # Setting time at the start of the decade
            'fields': {
                'value': metric,
                'country_name': country['name']
            }
        }
        points.append(point)
    logger.info(f'Writing decadal averages for {country["name"]} to DB')
    write_points_to_db(points, country)


def write_yoy_changes_to_db(country, yoy_changes, datatype):
    """
    Writes the Year-over-Year (YoY) changes to the DB for a specific country.

    :param dict country: The country information.
    :param dict yoy_changes: A dictionary containing the YoY changes.
    :param str datatype: The datatype for which to write the YoY changes.
    :return: None
    :rtype: None
    """
    points = []
    for year, changes in yoy_changes.items():
        for change in changes:
            if change is not None:
                from util import get_country_alpha_2
                point = {
                    'measurement': f'{MEASUREMENT_NAMES[datatype]}_yoy_change',
                    'tags': {
                        'country_id': get_country_alpha_2(country['name']),
                    },
                    'time': f"{year}-01-01T00:00:00Z",  # Setting time at the start of the year
                    'fields': {
                        'value': change,
                        'country_name': country['name']
                    }
                }
                points.append(point)
    logger.info(f'Writing {len(points)} YoY changes for {country["name"]} to DB')
    write_points_to_db(points, country)


def write_dod_changes_to_db(country, dod_changes, datatype):
    """
    Writes the Decade-over-Decade (DoD) changes to the DB for a specific country.

    :param dict country: The country information.
    :param dict dod_changes: A dictionary containing the DoD changes.
    :param str datatype: The datatype for which to write the DoD changes.
    :return: None
    :rtype: None
    """
    points = []
    for decade, changes in dod_changes.items():
        for change in changes:
            if change is not None:
                from util import get_country_alpha_2
                point = {
                    'measurement': f'{MEASUREMENT_NAMES[datatype]}_dod_change',
                    'tags': {
                        'country_id': get_country_alpha_2(country['name']),
                    },
                    'time': f"{decade}-01-01T00:00:00Z",  # Setting time at the start of the decade
                    'fields': {
                        'value': change,
                        'country_name': country['name']
                    }
                }
                points.append(point)
    logger.info(f'Writing {len(points)} DoD changes for {country["name"]} to DB')
    write_points_to_db(points, country)


def calculate_correct_metric(values, datatype):
    if datatype == 'TAVG' or datatype == 'PRCP':
        return sum(values) / len(values)
    elif datatype == 'TMAX' or datatype == 'EMXT' or datatype == 'EMXP' or datatype == 'EMSD':
        return max(values)
    elif datatype == 'TMIN' or datatype == 'EMNT':
        return min(values)
    else:
        raise ValueError(f'Unknown datatype {datatype}')


def drop_analysis_data(country):
    """
    Drop all analysis data for a country.

    :param dict country: The country for which to drop analysis data.
    :return: None
    :rtype: None
    """
    logger.info(f'Dropping analysis data for {country["name"]} from DB')
    from util import get_country_alpha_2

    for datatype in MEASUREMENT_NAMES.keys():
        drop(get_country_alpha_2(country['name']), f'{MEASUREMENT_NAMES[datatype]}_trend')
        drop(get_country_alpha_2(country['name']), f'{MEASUREMENT_NAMES[datatype]}_monthly_average')
        drop(get_country_alpha_2(country['name']), f'{MEASUREMENT_NAMES[datatype]}_yearly_average')
        drop(get_country_alpha_2(country['name']), f'{MEASUREMENT_NAMES[datatype]}_decadal_average')
        drop(get_country_alpha_2(country['name']), f'{MEASUREMENT_NAMES[datatype]}_dod_change')
        drop(get_country_alpha_2(country['name']), f'{MEASUREMENT_NAMES[datatype]}_yoy_change')
