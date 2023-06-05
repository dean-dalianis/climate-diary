import json
import logging
import os
import time
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm

LOGS_DIR = 'logs'
DATA_DIR = 'data'

# Create logs and data folders if they don't exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a file handler for INFO level logs
info_handler = logging.FileHandler(f"{LOGS_DIR}/app.log")
info_handler.setLevel(logging.INFO)

# Create another file handler for ERROR level logs
error_handler = logging.FileHandler(f"{LOGS_DIR}/error.log")
error_handler.setLevel(logging.WARNING)

# Create a formatter and set it for all handlers
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
info_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(info_handler)
logger.addHandler(error_handler)

# Constants
HEADERS = {
    # "token": "MMbckUthGxPJhtXxxBQlxNrqnmTtvQTf"
    "token": "CrowgJSXkoziFSVNtUXpQdvPibUoqGPK"
}
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/"
MAX_REQUESTS_PER_SECOND = 5
REQUESTS_INTERVAL = 1.0 / MAX_REQUESTS_PER_SECOND
DATATYPE_ID = "TMAX,TMIN,TAVG,PRCP,SNOW,EVAP,WDMV,AWND,WSF2,WSF5,WSFG,WSFI,WSFM,DYFG,DYHF,DYTS,RHAV"
BLACKLIST_FILE = 'blacklist_urls.json'

last_request_time = None

# Configure retries
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


def load_blacklist():
    """
    Load the list of blacklisted URLs from a JSON file.

    Returns:
        list: The list of blacklisted URLs.
    """
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'r') as file:
            return json.load(file)
    else:
        return []


def save_to_blacklist(url):
    """
    Add a URL to the blacklist and save the updated blacklist to a JSON file.

    Args:
        url (str): The URL to be added to the blacklist.
    """
    blacklist = load_blacklist()
    if url not in blacklist:
        blacklist.append(url)
    with open(BLACKLIST_FILE, 'w') as file:
        json.dump(blacklist, file)


def calculate_time_for_next_request():
    """
    Calculate the time to wait before making the next request, based on the rate limit.
    """
    global last_request_time

    # Check if rate limit needs to be enforced
    if last_request_time is not None:
        elapsed_time = time.time() - last_request_time
        if elapsed_time < REQUESTS_INTERVAL:
            time.sleep(REQUESTS_INTERVAL - elapsed_time)


def make_api_request(url):
    """
    Make an API request to the given URL.

    Args:
        url (str): The URL for the API request.

    Returns:
        dict: The response JSON data if the request is successful, None otherwise.
    """
    blacklist = load_blacklist()
    if url in blacklist:
        logger.info(f"Skipping blacklisted URL: {url}")
        return None

    calculate_time_for_next_request()

    logger.info(f"Making request to {url}")
    response = http.get(url, headers=HEADERS)
    global last_request_time
    last_request_time = time.time()  # Update the last request time
    logger.info(f"Received response from {url} with status code {response.status_code}")

    return handle_response(response, url)


def handle_response(response, url):
    """
    Handle the API response.

    Args:
        response (requests.Response): The API response object.
        url (str): The URL for the API request.

    Returns:
        dict: The response JSON data if the request is successful, None otherwise.
    """
    if response.status_code == 200:
        data = response.json()
        if 'results' in data:
            return data['results']
        else:
            logger.error(f"Request to {url} didn't have any 'results'")
            save_to_blacklist(url)
            return None
    else:
        logger.error(f"Request to {url} failed with status code {response.status_code}")
        save_to_blacklist(url)
        log_request_error(url, response.status_code)
        return None


def save_data_to_file(data, file_path):
    """
    Save data to a JSON file.

    Args:
        data (list or dict): The data to be saved.
        file_path (str): The path to the JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(data, file)


def load_or_fetch_data(fetch_func, file_path, *fetch_func_args):
    """
    Load data from a file or fetch it using the provided fetch function.

    Args:
        fetch_func (function): The function to fetch the data if the file doesn't exist.
        file_path (str): The path to the JSON file.
        *fetch_func_args: Arguments to pass to the fetch function.

    Returns:
        list or dict: The loaded or fetched data.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        data = fetch_func(*fetch_func_args)
        if data is not None:
            with open(file_path, 'w') as file:
                json.dump(data, file)
        return data


def get_countries():
    """
    Fetch the list of countries with climate data from the API.

    Returns:
        list: The list of countries.
    """
    countries_url = f"{BASE_URL}locations?datasetid=GSOM&locationcategoryid=CNTRY&limit=1000"
    return make_api_request(countries_url)


def get_climate_data(country_id, start_date, end_date):
    """
    Fetch climate data for a specific country within the specified date range.

    Args:
        country_id (str): The ID of the country.
        start_date (datetime): The start date of the data.
        end_date (datetime): The end date of the data.

    Returns:
        list: The climate data for the country.
    """
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    data_url = f"{BASE_URL}data?datasetid=GSOM&datatypeid={DATATYPE_ID}&units=metric&locationid={country_id}&startdate={start_date_str}&enddate={end_date_str}&limit=1000"
    return make_api_request(data_url)


def is_end_date_correct(file_path, actual_end_date):
    """
    Check if the end date in the data file matches the actual end date.

    Args:
        file_path (str): The path to the JSON data file.
        actual_end_date (datetime): The actual end date to compare.

    Returns:
        bool: True if the end date is correct, False otherwise.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            if len(data) > 0:
                last_data_point = data[-1]
                last_data_point_date = datetime.strptime(last_data_point['date'], '%Y-%m-%dT%H:%M:%S')
                return last_data_point_date.date() == actual_end_date.date()
    return False


def fetch_climate_data_for_country(country):
    """
    Fetch climate data for a specific country.

    Args:
        country (dict): The country data.

    Returns:
        None
    """
    max_records_per_request = 1000
    max_year_gap = 10

    # Convert dates to datetime objects
    min_date = datetime.strptime(country['mindate'], '%Y-%m-%d')
    max_date = datetime.strptime(country['maxdate'], '%Y-%m-%d')

    # Load climate data from file
    file_path = f"{DATA_DIR}/climate_data_{country['id'].replace(':', '_')}.json"
    climate_data = load_or_fetch_data(get_climate_data, file_path, country['id'], min_date, max_date)

    if climate_data is not None:
        country['climate_data'] = climate_data
        logger.info(f"Climate data loaded for country {country['name']}.")
        if is_end_date_correct(file_path, max_date):
            logger.info(f"Climate data for country {country['name']} is up to date.")
            return

    logger.info(f"Fetching climate data for {country['name']}")

    start_date = min_date

    while start_date <= max_date:
        end_date = min(start_date + relativedelta(years=max_year_gap), max_date)

        new_climate_data = get_climate_data(country['id'], start_date, end_date)
        if new_climate_data is None:
            break

        # Add country_id and country_name to each record in new_climate_data
        for record in new_climate_data:
            record['country_id'] = country['id']
            record['country_name'] = country['name']

        if 'climate_data' in country:
            country['climate_data'].extend(new_climate_data)
        else:
            country['climate_data'] = new_climate_data

        start_date = end_date + relativedelta(days=1)

    save_data_to_file(country['climate_data'], file_path)

    if is_end_date_correct(file_path, max_date):
        logger.info(f"Climate data fetched for country {country['name']}.")
    else:
        logger.warning(f"Failed to fetch complete climate data for country {country['name']}.")


def log_request_error(url, status_code):
    """
    Log a non-200 request to the `error.log` file.

    Args:
        url (str): The URL of the request.
        status_code (int): The status code of the response.
    """
    logger.error(f'Non-200 request. URL: {url} - Status Code: {status_code}')


def log_no_results(data_url):
    """
    Log a request with no results to the `no_results.log` file.

    Args:
        data_url (str): The URL of the request.
    """
    logger.warning(f'No results for request: {data_url}')


def noaa_gsom_fetcher():
    """
    The main entry point of the script.
    """
    # Create logs and data folders if they don't exist
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    countries = load_or_fetch_data(get_countries, f"{DATA_DIR}/countries.json")

    with tqdm(total=len(countries), desc="Fetching climate data") as pbar:
        for country in countries:
            fetch_climate_data_for_country(country)
            pbar.update()
    combine_all_climate_data(countries)


def combine_all_climate_data(countries):
    """
    Combine all climate data into a single JSON file.

    Args:
        countries (list): The list of countries.

    Returns:
        None
    """
    all_climate_data = []
    for country in countries:
        file_path = f"{DATA_DIR}/climate_data_{country['id'].replace(':', '_')}.json"
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
                all_climate_data.extend(data)

    with open(f"{DATA_DIR}/all_climate_data.json", 'w') as file:
        json.dump(all_climate_data, file)


if __name__ == "__main__":
    noaa_gsom_fetcher()