from influx import write_points_to_db, drop
from logging_config import logger


def analyze_data_and_write_to_db(country_iso, country_name, measurement, data):
    """
    Analyze the data and write the results to the database.
    Analyzed data includes:
        - decadal averages
        - year-over-year changes
        - decade-over-decade changes
        - trends

    :param str country_iso: The country iso to analyze.
    :param str country_name: The country name to analyze.
    :param str measurement: The measurement we're doing the analysis for
    :param list data: A list of dictionaries with data
    :return: None
    :rtype: None
    """

    trend_points = calculate_trend_points(country_iso, country_name, data, measurement)
    decadal_averages = calculate_decadal_averages(country_iso, country_name, data, measurement)
    yoy_changes = calculate_yoy_changes(country_iso, country_name, data, measurement)
    dod_changes = calculate_dod_changes(country_iso, country_name, data, measurement)

    write_points_to_db(trend_points)
    write_points_to_db(decadal_averages)
    write_points_to_db(dod_changes)
    write_points_to_db(yoy_changes)


def calculate_yoy_changes(country_iso, country_name, data, measurement):
    """
    Calculates the year-over-year (YoY) changes for the data, and prepare points to write to DB.

    :param str country_iso: The country iso to analyze.
    :param str country_name: The country name to analyze.
    :param list data: A list of dictionaries with data
    :param str measurement: The measurement we're doing the analysis for
    :return: A list of dictionaries with prepared points for YoY changes.
    :rtype: list
    """
    yoy_changes = {}
    sorted_data = sorted(data, key=lambda d: d['year'])  # Sort data points by year

    for i in range(1, len(sorted_data)):
        current_year = sorted_data[i]['year']
        yoy_change = sorted_data[i]['value'] - sorted_data[i - 1]['value']
        yoy_changes.setdefault(current_year, []).append(yoy_change)

    # Prepare points to write to DB for YoY changes
    yoy_points = []
    for year, changes in yoy_changes.items():
        for change in changes:
            if change is not None:
                point = {
                    'measurement': f'{measurement}_yoy_change',
                    'tags': {
                        'country_iso': country_iso
                    },
                    'time': f"{year}-01-01T00:00:00Z",  # Setting time at the start of the year
                    'fields': {
                        'value': change,
                        'country_name': country_name
                    }
                }
                yoy_points.append(point)

    return yoy_points


def calculate_dod_changes(country_iso, country_name, data, measurement):
    """
    Calculates the decade-over-decade (DoD) changes for the data, and prepare points to write to DB.

    :param str country_iso: The country iso to analyze.
    :param str country_name: The country name to analyze.
    :param list data: A list of dictionaries with data.
    :param str measurement: The measurement we're doing the analysis for
    :return: A list of dictionaries with prepared points for DoD changes.
    :rtype: list
    """
    dod_changes = {}
    sorted_data = sorted(data, key=lambda d: d['year'])  # Sort data points by year

    for i in range(1, len(sorted_data)):
        current_decade = (sorted_data[i]['year'] // 10) * 10
        prev_decade = (sorted_data[i - 1]['year'] // 10) * 10
        dod_change = sorted_data[i]['value'] - sorted_data[i - 1]['value'] if current_decade == prev_decade else None
        dod_changes.setdefault(current_decade, []).append(dod_change)

    # Prepare points to write to DB for DoD changes
    dod_points = []
    for decade, changes in dod_changes.items():
        change = sum(x for x in changes if x is not None)
        if change is not None:
            point = {
                'measurement': f'{measurement}_dod_change',
                'tags': {
                    'country_iso': country_iso
                },
                'time': f"{decade}-01-01T00:00:00Z",  # Setting time at the start of the decade
                'fields': {
                    'value': change,
                    'country_name': country_name
                }
            }
            dod_points.append(point)

    return dod_points


def calculate_trend_points(country_iso, country_name, data, measurement):
    """
    Calculates the trend points for the data.

    :param str country_iso: The country iso for which to calculate trends.
    :param str country_name: The country name for which to calculate trends.
    :param list data: A list of dictionaries with data
    :param str measurement: The measurement we're doing the analysis for
    :return: A list of dictionaries with trend points.
    :rtype: list
    """
    import numpy as np

    timestamps = [d['year'] for d in data]
    values = [d['value'] for d in data]
    trend_slope, trend_intercept = np.polynomial.polynomial.polyfit(timestamps, values, 1)

    trend_points = []
    for i, timestamp in enumerate(timestamps):
        trend_point = {
            'measurement': f'{measurement}_trend',
            'tags': {
                'country_iso': country_iso,
            },
            'time': str(data[i]['year']),  # convert the year to string
            'fields': {
                'value': trend_slope * timestamp + trend_intercept,
                'country_name': country_name,
            }
        }
        trend_points.append(trend_point)

    return trend_points


def calculate_decadal_averages(country_iso, country_name, data, measurement):
    """
    Calculates the decadal averages for the data and prepare points to write to DB.

    :param str country_iso: The country iso for which to calculate decadal averages.
    :param str country_name: The country name for which to calculate decadal averages.
    :param list data: A list of dictionaries with data.
    :param str measurement: The measurement for which to write the decadal averages.
    :return: A list of dictionaries with prepared points.
    :rtype: list
    """

    # Calculate decadal averages
    decadal_averages = {}
    for d in data:
        year, value = d['year'], d['value']
        decade = (year // 10) * 10

        decadal_averages.setdefault(decade, []).append(value)

    for decade, values in decadal_averages.items():
        decadal_averages[decade] = sum(values) / len(values)

    # Prepare points to write to DB
    points = []
    for decade, average in decadal_averages.items():
        metric = calculate_correct_metric(average, measurement)  # adjust this if calculate_correct_metric() is not the right function for this
        point = {
            'measurement': f'{measurement}_decadal_average',
            'tags': {
                'country_id': country_iso,
            },
            'time': f"{decade}-01-01T00:00:00Z",  # Setting time at the start of the decade
            'fields': {
                'value': metric,
                'country_name': country_name,
            }
        }
        points.append(point)

    return points


def calculate_correct_metric(values, datatype):
    if datatype == 'TAVG' or datatype == 'PRCP':
        return sum(values) / len(values)
    elif datatype == 'TMAX' or datatype == 'EMXT' or datatype == 'EMXP' or datatype == 'EMSD':
        return max(values)
    elif datatype == 'TMIN' or datatype == 'EMNT':
        return min(values)
    else:
        raise ValueError(f'Unknown datatype {datatype}')
