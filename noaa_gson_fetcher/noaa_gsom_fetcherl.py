import logging
import time
from datetime import datetime, timedelta

import requests
from dateutil.parser import parse
from influxdb import InfluxDBClient
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm

INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = '8086'
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = '<influx_pwd>'
INFLUXDB_DATABASE = 'climate'
BATCH_SIZE = 50  # Number of countries to process at a time

BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/"
DATATYPE_ID = "TMAX,TMIN,TAVG,PRCP,SNOW,EVAP,WDMV,AWND,WSF2,WSF5,WSFG,WSFI,WSFM,DYFG,DYHF,DYTS,RHAV"
ATTRIBUTES = {
    "TMAX": ["days_missing", "measurement_flag", "quality_flag", "source_code"],
    "TMIN": ["days_missing", "measurement_flag", "quality_flag", "source_code"],
    "TAVG": ["days_missing", "source_code"],
    "PRCP": ["days_missing", "measurement_flag", "quality_flag", "source_code"],
    "SNOW": ["days_missing", "measurement_flag", "quality_flag", "source_code"],
    "EVAP": ["days_missing", "measurement_flag", "quality_flag", "source_code"],
    "WDMV": ["days_missing", "measurement_flag", "quality_flag", "source_code"],
    "AWND": ["days_missing", "source_code"],
    "WSF2": ["days_missing", "source_code"],
    "WSF5": ["days_missing", "source_code"],
    "WSFG": ["days_missing", "source_code"],
    "WSFI": ["days_missing", "source_code"],
    "WSFM": ["days_missing", "source_code"],
    "DYFG": [],
    "DYHF": [],
    "DYTS": [],
    "RHAV": ["days_missing", "measurement_flag", "quality_flag", "source_code"],
}

HEADERS = {
    "token": "CrowgJSXkoziFSVNtUXpQdvPibUoqGPK"
    # "token": "MMbckUthGxPJhtXxxBQlxNrqnmTtvQTf"
}

last_request_time = None
MAX_REQUESTS_PER_SECOND = 5
REQUESTS_INTERVAL = 1.0 / MAX_REQUESTS_PER_SECOND

retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Setup logging
logging.basicConfig(filename='climate_data.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


def sleep_until_next_request():
    """
    Sleep until it's time for the next request, based on the maximum request rate.
    """
    global last_request_time
    if last_request_time is not None:
        elapsed_time = time.time() - last_request_time
        if elapsed_time < REQUESTS_INTERVAL:
            time.sleep(REQUESTS_INTERVAL - elapsed_time)


def make_api_request(url):
    """
    Make a GET request to the specified URL and return the JSON response.
    If the response status code is not 200, returns None.

    :param str url: The URL to send a GET request to.
    :return: The response to the request, in JSON format.
    :rtype: dict or None
    """
    sleep_until_next_request()
    response = http.get(url, headers=HEADERS)
    global last_request_time
    last_request_time = time.time()
    if response.status_code == 200:
        json_data = response.json()
        if 'results' in json_data:
            return json_data['results']
        else:
            return None
    else:
        logging.error(f'Received status code {response.status_code} for URL {url}')
        return None


def get_countries():
    """
    Fetch and return a list of countries.

    :return: A list of countries.
    :rtype: list or None
    """
    countries_url = f"{BASE_URL}locations?datasetid=GSOM&locationcategoryid=CNTRY&limit=1000"
    countries = make_api_request(countries_url)
    if countries is None:
        logging.error('Failed to fetch countries')
    return countries


def get_climate_data(country_id, start_date, end_date):
    """
    Fetch and return climate data for the specified country and date range.

    :param str country_id: The ID of the country to fetch data for.
    :param datetime start_date: The start of the date range.
    :param datetime end_date: The end of the date range.
    :return: Climate data for the specified country and date range.
    :rtype: list or None
    """
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    data_url = f"{BASE_URL}data?datasetid=GSOM&datatypeid={DATATYPE_ID}&units=metric&locationid={country_id}&startdate={start_date_str}&enddate={end_date_str}&limit=1000"
    data = make_api_request(data_url)
    if data is None:
        logging.error(f'Failed to fetch climate data for country {country_id} from {start_date_str} to {end_date_str}')
    return data


def get_last_record_date_for_country(country_id, client):
    """
    Fetch and return the date of the last record for the specified country.

    :param str country_id: The ID of the country.
    :param InfluxDBClient client: The InfluxDB client.
    :return: The date of the last record for the country.
    :rtype: datetime.datetime or None
    """
    result = client.query(
        f'SELECT last("value") FROM "climate" WHERE "country_id" = \'{country_id}\'')
    if result:
        last_time = list(result.get_points(measurement='climate'))[0]['time']
        return parse(last_time)
    return None


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


def fetch_and_write_climate_data_to_influxdb():
    """
    Main function - Connects to InfluxDB and fetches climate data for each country, writing it to the database.
    """
    client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT,
        username=INFLUXDB_USER,
        password=INFLUXDB_PASSWORD,
        database=INFLUXDB_DATABASE
    )

    countries = get_countries()
    if countries is not None:
        for i in tqdm(range(0, len(countries), BATCH_SIZE), desc="Fetching climate data"):
            batch_countries = countries[i:i + BATCH_SIZE]
            points = []
            for country in batch_countries:
                last_record_date = get_last_record_date_for_country(country['id'], client)

                if last_record_date is None:
                    start_date = datetime.strptime(country['mindate'], '%Y-%m-%d')
                else:
                    start_date = last_record_date + timedelta(days=1)

                end_date = datetime.strptime(country['maxdate'], '%Y-%m-%d')

                while start_date <= end_date:
                    current_end_date = min(start_date + timedelta(days=3652),
                                           end_date)  # 10 years from start_date or end_date, whichever is earlier
                    climate_data = get_climate_data(country['id'], start_date, current_end_date)
                    if climate_data is not None:
                        for record in climate_data:
                            fields = {
                                "value": record['value']
                            }
                            if 'attributes' in record:
                                fields.update(decode_attributes(record['datatype'], record['attributes']))

                            points.append({
                                "measurement": "climate",
                                "tags": {
                                    "country_name": country['name'],
                                    "country_id": country['id'],
                                    "datatype": record['datatype']
                                },
                                "time": parse(record['date']).isoformat(),
                                "fields": fields
                            })

                    # Adjust the start_date for the next iteration
                    start_date = current_end_date + timedelta(days=1)

            # Write points for all countries in the batch
            if points:
                try:
                    client.write_points(points)
                    logging.info(f'Successfully wrote data for countries {i}-{i + BATCH_SIZE - 1}')
                except Exception as e:
                    logging.error(f'Failed to write data for countries {i}-{i + BATCH_SIZE - 1}: {str(e)}')
            else:
                logging.error('No data to write')
        else:
            logging.error('Could not fetch the list of countries')


if __name__ == "__main__":
    fetch_and_write_climate_data_to_influxdb()
