import json
import os
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from logging_config import logger

TOKENS = [os.environ.get(f'NOAA_TOKEN_{i}') for i in range(1, 7)]

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config/api_config.json')
with open(CONFIG_FILE, 'r') as file:
    config = json.load(file)

BASE_URL = config['BASE_URL']
MAX_REQUESTS_PER_TOKEN = config['MAX_REQUESTS_PER_TOKEN']
MAX_REQUESTS_PER_SECOND = config['MAX_REQUESTS_PER_SECOND']

REQUESTS_INTERVAL = 1.0 / MAX_REQUESTS_PER_SECOND

current_token_index = 0
current_token_requests = 0
last_request_time = 0.0

retry_strategy = Retry(
    total=5,
    status_forcelist=[500, 502, 503, 504],
    backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)


def update_token():
    """
    Update the current token index and reset the number of requests for the token.

    :return: None
    :rtype: None
    """
    global current_token_index, current_token_requests
    current_token_index = (current_token_index + 1) % len(TOKENS)
    current_token_requests = 0


def get_headers():
    """
    Get the headers for making an API request, including the current token.

    :return: The headers for making an API request.
    :rtype: dict
    """
    global current_token_requests
    current_token_requests += 1
    if current_token_requests > MAX_REQUESTS_PER_TOKEN:
        logger.info(f'Token {current_token_index} reached {current_token_requests} requests. Changing token...')
        update_token()
    return {
        "token": TOKENS[current_token_index]
    }


def sleep_until_next_request():
    """
    Sleep until it's time for the next request, based on the maximum request rate.

    :return: None
    :rtype: None
    """
    global last_request_time
    if last_request_time is not None:
        elapsed_time = time.time() - last_request_time
        if elapsed_time < REQUESTS_INTERVAL:
            time.sleep(REQUESTS_INTERVAL - elapsed_time)


def do_get(url):
    global last_request_time

    while True:
        try:
            sleep_until_next_request()
            response = http.get(url, headers=get_headers())
            last_request_time = time.time()
            if response.status_code == 429:
                logger.warning(f'Rate limit reached for token {current_token_index} - retrying with new token...')
                if current_token_index == 7:
                    logger.error('All tokens have been used. Exiting...')
                    exit(1)
                update_token()
                continue
            return response
        except Exception as e:
            last_request_time = time.time()
            logger.warning(f'Connection error occurred: {e} - retrying with new token...')
            if current_token_index == 7:
                logger.error('All tokens have been used. Exiting...')
                exit(1)
            update_token()


def make_api_request(url, offset):
    """
    Make an API request to the specified URL, handling rate limiting and token rotation.

    :param str url: The URL to make the API request to.
    :return: The JSON response from the API request, and a boolean indicating if there is more data.
    :rtype: list, bool
    """

    paged_url = f'{BASE_URL}{url}&offset={offset}'
    response = do_get(paged_url)

    if response.status_code == 200:
        json_data = response.json()

        if 'results' in json_data:
            results = json_data['results']

            # Calculate total number of results
            total_count = json_data.get('metadata', {}).get('resultset', {}).get('count', 0)

            # Check if there are more results to fetch
            if total_count > offset + len(results):
                return results, True
            else:
                # All results have been fetched
                return results, False
        else:
            logger.error(
                f'No \'results\' in response for URL {paged_url}. Response content: {response.content}')
    else:
        logger.error(
            f'Received status code {response.status_code} for URL {paged_url}. Response content: {response.content}.')

    return None, False
