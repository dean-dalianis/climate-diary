from config import BUCKET, GSOY_MEASUREMENTS, ISO_MAPPING
from flask import g
from logging_config import logger


def fetch_data(country_iso=None, measurement=None, date=None, start_date=None, end_date=None, decade_flag=False):
    """
    Fetch climate data for a specified country or all countries based on given conditions.
    If decade_flag is set to True, data will be fetched for decades.
    """
    records = []

    if measurement:
        if measurement not in GSOY_MEASUREMENTS:
            logger.error(f"Invalid measurement: {measurement}")
            return None
        measurement_names = [measurement]
    else:
        measurement_names = GSOY_MEASUREMENTS

    for measurement in measurement_names:
        query = f'from(bucket: "{BUCKET}") |> range(start: 0) |> filter(fn: (r) => r["_measurement"] == "{measurement}")'

        if country_iso is not None:
            query += f' |> filter(fn: (r) => r["country_iso"] == "{country_iso}")'

        if date:
            query += f' |> filter(fn: (r) => r["_time"] >= time(v: "{date}T00:00:00Z") and r["_time"] <= time(v: "{date}T23:59:59Z"))'
        elif start_date and end_date:
            query += f' |> filter(fn: (r) => r["_time"] >= time(v: "{start_date}T00:00:00Z") and r["_time"] <= time(v: "{end_date}T23:59:59Z"))'

        tables = g.query_api.query(query)

        logger.info(f'Retrieved {len(tables)} tables for measurement: {measurement}')

        for table in tables:
            for record in table.records:
                entry = {
                    'measurement': measurement,
                    'country_iso': record.values.get('country_iso'),
                    'country_name': ISO_MAPPING[record.values.get('country_iso')],
                    'value': record.get_value(),
                    'time': record.get_time()
                }
                records.append(entry)

        if not records:
            if date:
                logger.warning(f"No data found in DB for measurement: {measurement}, and date: {date}")
            elif start_date and end_date:
                logger.warning(
                    f"No data found in DB for measurement: {measurement}, and range: {start_date} to {end_date}")
            else:
                logger.warning(f"No data found in DB for measurement: {measurement}")

    if records:
        return records
    else:
        if date:
            logger.warning(f"No data found in DB for date: {date}")
        elif start_date and end_date:
            logger.warning(f"No data found in DB for range: {start_date} to {end_date}")
        else:
            logger.warning(f"No data found in DB")
        return None
