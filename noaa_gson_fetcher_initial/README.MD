# NOAA GSOM fetcher

Climate Data Fetcher is a Python script that fetches and stores historical climate data from the Global Summary of the
Month (GSOM) dataset in NOAA's Climate Data Online (CDO) API. It downloads data such as daily maximum and minimum
temperatures, average temperature, precipitation, snowfall, and other metrics for all available countries. The script
manages API request rate limiting and handles possible API response errors.

## Data Types

The script fetches the following data types from the API:

- `TMAX`: Maximum temperature
- `TMIN`: Minimum temperature
- `TAVG`: Average temperature
- `PRCP`: Precipitation
- `SNOW`: Snowfall
- `EVAP`: Evaporation
- `WDMV`: Wind movement
- `AWND`: Average daily wind speed
- `WSF2`: Fastest 2-minute wind speed
- `WSF5`: Fastest 5-second wind speed
- `WSFG`: Peak gust wind speed
- `WSFI`: Fastest instantaneous wind speed
- `WSFM`: Fastest 5-minute wind speed
- `DYFG`: Days with fog
- `DYHF`: Days with heat index >= 90F/32.2C
- `DYTS`: Days with thunder
- `RHAV`: Average relative humidity

Each of these data types is included in the `DATATYPE_ID` constant at the top of the script. If you want to fetch
different data types, modify this constant accordingly.

## Requirements

- Python 3.8 or later
- requests package (Install with `pip install requests`)
- python-dateutil package (Install with `pip install python-dateutil`)
- tqdm package (Install with `pip install tqdm`)

## Usage

1. Set your API token in the `HEADERS` constant at the top of the script.

    ```python
    HEADERS = {
        "token": "your_api_token_here"
    }
    ```

2. Run the script from the command line:

    ```bash
    python climate_data_fetcher.py
    ```

   The script will start fetching climate data for all countries. Progress will be shown in the console.

3. The fetched data is saved to the `data` folder as JSON files. Each country's data is saved in a separate file
   named `climate_data_{country_id}.json`.

4. Errors and warnings are logged to the `logs` folder. There are three types of log files:

    - `app.log`: General application log.
    - `error.log`: Logs of failed API requests.
    - `no_results.log`: Logs of API requests that returned no results.

## Blacklisting URLs

The script maintains a list of blacklisted URLs (URLs that have previously returned an error or no results). If a
request to a blacklisted URL is to be made, the request is skipped. The blacklist is stored in the `blacklist_urls.json`
file in the main script folder. You can manually add or remove URLs from the blacklist.

## Rate Limiting

The script manages rate limiting based on the `MAX_REQUESTS_PER_SECOND` constant. By default, it is set to 5 requests
per second.

## Fetching Specific Date Ranges

The script fetches data for the entire available date range for each country. If you want to fetch data for a specific
date range, modify the `fetch_climate_data_for_country` function accordingly.

## Note

This is an unofficial script and is not affiliated with or endorsed by NOAA. Always check
the [NOAA's API terms of service](https://www.ncdc.noaa.gov/cdo-web/webservices/v2) before using the script.

## License

This project is licensed under the terms of the MIT license.
