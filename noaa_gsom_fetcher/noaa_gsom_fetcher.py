import logging
import os
import time
from datetime import datetime, timedelta, timezone
from logging.handlers import TimedRotatingFileHandler
from zoneinfo import ZoneInfo

import requests
from dateutil.parser import parse
from influxdb import InfluxDBClient
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

INFLUXDB_HOST = 'influxdb'
INFLUXDB_PORT = '8086'

INFLUXDB_DATABASE = os.environ.get('INFLUXDB_DB')
INFLUXDB_USER = os.environ.get('INFLUXDB_ADMIN_USER')
INFLUXDB_PASSWORD = os.environ.get('INFLUXDB_ADMIN_PASSWORD')

BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/"
DATATYPE_ID = "TMAX,TMIN,TAVG,PRCP,SNOW,EVAP,WDMV,AWND,WSF2,WSF5,WSFG,WSFI,WSFM,DYFG,DYHF,DYTS,RHAV"

EU_CONTINENT_FIPS = ["AL", "AN", "AU", "BO", "BE", "BU", "HR", "CY", "EZ", "DA", "EN", "FI", "FR", "GM", "GR", "HU",
                     "IC", "EI", "IT", "KV", "LG", "LH", "LU", "MK", "MT", "MD", "MN", "NL", "NO", "PL", "PO", "RO",
                     "RI", "LO", "SI", "SP", "SW", "SZ", "UK", "UP", "RS", "BO", "MD", "SM", "IM", "LI", "MC", "VA"]

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
    "DYTS": [],
    "RHAV": ["days_missing", "measurement_flag", "quality_flag", "source_code"]
}

MEASUREMENT_NAMES = {
    "TMAX": "Maximum Temperature",
    "TMIN": "Minimum Temperature",
    "TAVG": "Average Temperature",
    "PRCP": "Precipitation",
    "SNOW": "Snowfall",
    "EVAP": "Evaporation",
    "WDMV": "Wind Movement",
    "AWND": "Average Daily Wind Speed",
    "WSF2": "Fastest 2-Minute Wind Speed",
    "WSF5": "Fastest 5-Second Wind Speed",
    "WSFG": "Peak Gust Wind Speed",
    "WSFI": "Fastest Instantaneous Wind Speed",
    "WSFM": "Fastest 5-Minute Wind Speed",
    "DYFG": "Days with Fog",
    "DYTS": "Days with Thunder",
    "RHAV": "Average Relative Humidity"
}

MIN_START_YEAR = 1940

# Store your tokens in a list
TOKENS = [os.environ.get(f'NOAA_TOKEN_{i}') for i in range(1, 6)]

# Use a variable to track the current token index and request count
current_token_index = 0
current_token_requests = 0
MAX_REQUESTS_PER_TOKEN = 10000


def update_token():
    global current_token_index, current_token_requests
    current_token_index = (current_token_index + 1) % len(TOKENS)
    current_token_requests = 0


def get_headers():
    global current_token_requests
    current_token_requests += 1
    if current_token_requests > MAX_REQUESTS_PER_TOKEN:
        logging.info(f'Token {current_token_index} reached {current_token_requests} requests. Changing token...')
        update_token()
    return {
        "token": TOKENS[current_token_index]
    }


last_request_time = None
MAX_REQUESTS_PER_SECOND = 5
REQUESTS_INTERVAL = 1.0 / MAX_REQUESTS_PER_SECOND

retry_strategy = Retry(
    total=5,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"],
    backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Set up log rotation
log_filename = 'log/climate_data.log'
log_handler = TimedRotatingFileHandler(log_filename, when='D', interval=1, backupCount=7)
log_handler.suffix = "%Y-%m-%d"
log_handler.setLevel(logging.INFO)

# Set up console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Set up logging format
log_format = '%(asctime)s %(levelname)s %(message)s'
log_formatter = logging.Formatter(log_format)
log_handler.setFormatter(log_formatter)
console_handler.setFormatter(log_formatter)

# Set up root logger
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


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
    offset = 0  # start with offset 0
    all_results = []

    while True:
        sleep_until_next_request()
        paged_url = f"{url}&offset={offset}"
        response = http.get(paged_url, headers=get_headers())
        last_request_time = time.time()

        if response.status_code == 200:
            json_data = response.json()

            if 'results' in json_data:
                results = json_data['results']
                all_results.extend(results)

                # Calculate total number of results
                total_count = json_data.get('metadata', {}).get('resultset', {}).get('count', 0)

                # Check if there are more results to fetch
                if total_count > offset + len(results):
                    offset += len(results)
                else:
                    # All results have been fetched
                    return all_results
            else:
                logging.error(
                    f'No \'results\' in response for URL {paged_url}. Response content: {response.content}')
                break  # Break from loop if no 'results' in response
        elif response.status_code == 429:
            logging.warning(
                f'Received status code {response.status_code} for URL {paged_url}. Changing token...')
            update_token()  # Update token if status code is 429
        else:
            logging.error(
                f'Received status code {response.status_code} for URL {paged_url}. Response content: {response.content}')
            break  # Break from loop if status code is not 200

    return all_results


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


def fetch_stations(country_id, start_date):
    """
    Fetches and returns a map of all stations for a given country.

    :param dict country_id: The country_id to fetch the stations for.
    :param datetime start_date: The start of the date range.
    :return: A map of stations. Each key is the id of the station, and its value is a dictionary containing the 'elevation', 'latitude', 'longitude', and 'name' of the station.
    :rtype: dict
    """
    start_date_str = start_date.strftime('%Y-%m-%d')
    stations_url = f"{BASE_URL}stations?datasetid=GSOM&&units=metric&locationid={country_id}&startdate={start_date_str}&limit=1000"
    stations = make_api_request(stations_url)

    logging.info(f'Fetching stations for {country_id}...')

    station_map = {}
    for station in stations:
        station_map[station['id']] = {
            'elevation': station.get('elevation', float('inf')),
            'latitude': station.get('latitude', float('inf')),
            'longitude': station.get('longitude', float('inf')),
            'name': station.get('name', 'N/A')
        }

    if len(stations) == 0:
        logging.error('Failed to fetch stations')
        return None

    logging.info(f'Fetched {len(station_map)} stations for {country_id}...')

    return station_map


def fetch_countries():
    """
    Fetch and return a list of all countries.

    :return: A list of countries.
    :rtype: list or None
    """
    logging.info(f'Fetching countries...')
    countries_url = f"{BASE_URL}locations?datasetid=GSOM&locationcategoryid=CNTRY&limit=1000"
    countries = make_api_request(countries_url)
    if len(countries) == 0:
        logging.error('Failed to fetch countries')
        return None

    logging.info(f'Fetched {len(countries)} countries.')

    return countries


def fetch_european_countries():
    all_countries = fetch_countries()
    european_countries = [country for country in all_countries if country['id'].split(':')[1] in EU_CONTINENT_FIPS]
    if len(european_countries) == 0:
        logging.error('Failed to fetch European countries')
        return None
    logging.info(f'Fetched {len(european_countries)} European countries.')
    return european_countries


def fetch_climate_data(country_id, start_date, end_date):
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


def fetch_and_write_climate_data_to_influxdb():
    """
    Connects to InfluxDB, fetches climate data for each country, writes them to the database.
    """
    client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT,
        username=INFLUXDB_USER,
        password=INFLUXDB_PASSWORD,
        database=INFLUXDB_DATABASE
    )

    countries = fetch_european_countries()

    if countries is None:
        return

    for country in countries:
        points = []
        logging.info(f'Fetching climate data for country: {country["name"]}')

        start_date = datetime.strptime(country['mindate'], '%Y-%m-%d').replace(tzinfo=ZoneInfo("UTC"))
        if start_date.year < MIN_START_YEAR:
            start_date = datetime(MIN_START_YEAR, 1, 1, tzinfo=ZoneInfo("UTC"))
        end_date = datetime.strptime(country['maxdate'], '%Y-%m-%d').replace(tzinfo=ZoneInfo("UTC"))
        print(start_date)
        station_map = fetch_stations(country['id'], start_date)

        while start_date <= end_date:
            current_end_date = min(start_date + timedelta(days=9 * 365),
                                   end_date)  # 9 years from start_date or end_date, whichever is earlier
            climate_data = fetch_climate_data(country['id'], start_date, current_end_date)
            if climate_data is not None:
                for record in climate_data:
                    station_details = station_map[record['station']]
                    fields = {
                        "value": float(record['value']),
                        "country_id": country['id'].split(':')[1],
                        "latitude": float(station_details['latitude']),
                        "longitude": float(station_details['longitude']),
                        "elevation": float(station_details['elevation'])
                    }
                    if 'attributes' in record:
                        fields.update(decode_attributes(record['datatype'], record['attributes']))

                    points.append({
                        "measurement": MEASUREMENT_NAMES.get(record['datatype']),
                        "tags": {
                            "country": country['name'],
                            "station": record['station'],
                            "station_name": station_details['name']
                        },
                        "time": parse(record['date']).astimezone(timezone.utc).isoformat(),
                        "fields": fields
                    })

            # Adjust the start_date for the next iteration
            start_date = current_end_date + timedelta(days=1)

        # Write points for all countries in the batch
        if points:
            try:
                logging.info(f'Writing data for {country["name"]}')
                client.write_points(points)
                logging.info(f'Successfully wrote data for {country["name"]}')
            except Exception as e:
                logging.error(f'Failed to write data for {country["name"]}, {e}')
        else:
            logging.error('No data to write')


def wait_for_influxdb():
    """
    Wait until the InfluxDB is ready to accept connections.
    """
    client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT,
        username=INFLUXDB_USER,
        password=INFLUXDB_PASSWORD,
        database=INFLUXDB_DATABASE
    )
    for i in range(30):  # try for 30 times
        try:
            client.ping()
            return
        except Exception as e:
            time.sleep(1)
    raise Exception("Cannot connect to InfluxDB")


if __name__ == "__main__":
    wait_for_influxdb()
    logging.info(f'Loaded token {TOKENS}')
    fetch_and_write_climate_data_to_influxdb()
