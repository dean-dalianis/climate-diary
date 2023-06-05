import json
import logging
import os.path
import time
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

headers = {
    # "token": "MMbckUthGxPJhtXxxBQlxNrqnmTtvQTf"
    "token": "CrowgJSXkoziFSVNtUXpQdvPibUoqGPK"
}

base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/"
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

country_statuses = []


def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'r') as file:
            return json.load(file)
    else:
        return []


def save_to_blacklist(url):
    blacklist = load_blacklist()
    if url not in blacklist:
        blacklist.append(url)
    with open(BLACKLIST_FILE, 'w') as file:
        json.dump(blacklist, file)


def calculate_time_for_next_request():
    global last_request_time

    # Check if rate limit needs to be enforced
    if last_request_time is not None:
        elapsed_time = time.time() - last_request_time
        if elapsed_time < REQUESTS_INTERVAL:
            time.sleep(REQUESTS_INTERVAL - elapsed_time)


def make_api_request(url):
    blacklist = load_blacklist()
    if url in blacklist:
        logging.info(f"Skipping blacklisted URL: {url}")
        return None

    calculate_time_for_next_request()

    logging.info(f"Making request to {url}")
    response = http.get(url, headers=headers)
    global last_request_time
    last_request_time = time.time()  # Update the last request time
    logging.info(f"Received response from {url} with status code {response.status_code}")

    return handle_response(response, url)


def handle_response(response, url):
    if response.status_code == 200:
        data = response.json()
        if 'results' in data:
            return data['results']
        else:
            logging.error(f"Request to {url} didn't have any 'results'")
            save_to_blacklist(url)
            return None
    else:
        logging.error(f"Request to {url} failed with status code {response.status_code}")
        save_to_blacklist(url)
        return None


def save_data_to_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file)


def load_or_fetch_data(fetch_func, file_path, *fetch_func_args):
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
    countries_url = f"{base_url}locations?datasetid=GSOM&locationcategoryid=CNTRY&limit=1000"
    return make_api_request(countries_url)


def get_climate_data(country_id, start_date, end_date):
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    data_url = f"{base_url}data?datasetid=GSOM&datatypeid={DATATYPE_ID}&units=metric&locationid={country_id}&startdate={start_date_str}&enddate={end_date_str}&limit=1000"
    return make_api_request(data_url)


def is_end_date_correct(file_path, actual_end_date):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            if len(data) > 0:
                last_data_point = data[-1]
                last_data_point_date = datetime.strptime(last_data_point['date'], '%Y-%m-%dT%H:%M:%S')
                return last_data_point_date.date() == actual_end_date.date()
    return False


def fetch_climate_data_for_country(country):
    max_records_per_request = 1000
    max_year_gap = 10

    # Convert dates to datetime objects
    mindate = datetime.strptime(country['mindate'], '%Y-%m-%d')
    maxdate = datetime.strptime(country['maxdate'], '%Y-%m-%d')

    # Load climate data from file
    file_path = f"climate_data_{country['id'].replace(':', '_')}.json"
    climate_data = load_or_fetch_data(get_climate_data, file_path, country['id'], mindate, maxdate)

    if climate_data is not None:
        country['climate_data'] = climate_data
        logging.info(f"Climate data loaded for country {country['name']}.")
        if is_end_date_correct(file_path, maxdate):
            logging.info(f"Climate data for country {country['name']} is up to date.")
            return

    logging.info(f"Fetching climate data for {country['name']}")

    startdate = mindate

    while startdate <= maxdate:
        enddate = min(startdate + relativedelta(years=max_year_gap), maxdate)

        new_climate_data = get_climate_data(country['id'], startdate, enddate)
        if new_climate_data is None:
            break

        if 'climate_data' in country:
            country['climate_data'].extend(new_climate_data)
        else:
            country['climate_data'] = new_climate_data

        startdate = enddate + relativedelta(days=1)

    save_data_to_file(country['climate_data'], file_path)

    if is_end_date_correct(file_path, maxdate):
        logging.info(f"Climate data fetched for country {country['name']}.")
    else:
        logging.warning(f"Failed to fetch complete climate data for country {country['name']}.")



def main():
    countries = load_or_fetch_data(get_countries, 'countries.json')

    with tqdm(total=len(countries), desc="Fetching climate data") as pbar:
        for country in countries:
            fetch_climate_data_for_country(country)
            pbar.update()

    country_statuses.sort(key=lambda x: (x[2], x[1]))

    # Write the statuses to a file
    with open('country_statuses.txt', 'w') as file:
        for name, id, status in country_statuses:
            file.write(f'{name} {id} {status}\n')


if __name__ == "__main__":
    main()
