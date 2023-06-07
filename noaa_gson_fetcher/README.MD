# NOAA GSOM fetcher

Climate Data Fetcher is a Python script that fetches and stores historical climate data from the Global Summary of the
Month (GSOM) dataset in NOAA's Climate Data Online (CDO) API. It downloads data such as daily maximum and minimum
temperatures, average temperature, precipitation, snowfall, and other metrics for all available countries. The fetched
data is written directly to an InfluxDB instance. The script manages API request rate limiting and handles possible API
response errors.

## Data Types and Attribute Decoding

The script fetches various types of climate data, each of which may have associated attributes. These attributes provide additional information about the data. For example, the number of days a particular measurement was missing, any measurement or quality flags, and source codes.

Below are the data types the script fetches and the associated attributes:

- TMAX: Maximum temperature. Attributes: days_missing, measurement_flag, quality_flag, source_code
- TMIN: Minimum temperature. Attributes: days_missing, measurement_flag, quality_flag, source_code
- TAVG: Average temperature. Attributes: days_missing, source_code
- PRCP: Precipitation. Attributes: days_missing, measurement_flag, quality_flag, source_code
- SNOW: Snowfall. Attributes: days_missing, measurement_flag, quality_flag, source_code
- EVAP: Evaporation. Attributes: days_missing, measurement_flag, quality_flag, source_code
- WDMV: Wind movement. Attributes: days_missing, measurement_flag, quality_flag, source_code
- AWND: Average daily wind speed. Attributes: days_missing, source_code
- WSF2: Fastest 2-minute wind speed. Attributes: days_missing, source_code
- WSF5: Fastest 5-second wind speed. Attributes: days_missing, source_code
- WSFG: Peak gust wind speed. Attributes: days_missing, source_code
- WSFI: Fastest instantaneous wind speed. Attributes: days_missing, source_code
- WSFM: Fastest 5-minute wind speed. Attributes: days_missing, source_code
- DYFG: Days with fog. Attributes: None
- DYHF: Days with heat index >= 90F/32.2C. Attributes: None
- DYTS: Days with thunder. Attributes: None
- RHAV: Average relative humidity. Attributes: days_missing, measurement_flag, quality_flag, source_code

The decode_attributes function in the script takes care of decoding these attributes from the API response and storing them in the InfluxDB along with the corresponding data.

For any new data type that you want to fetch, ensure that you add the associated attributes to the ATTRIBUTES dictionary in the script.

Please note that the 'source_code' attribute, if present, is excluded during the attribute decoding process.

## Requirements

This project requires Python 3.8 or later.

All Python packages required for this script are listed in the requirements.txt file. You can install these packages
using pip by running the following command:

   ```bash
   pip install -r requirements.txt
  ````

In addition to these packages, you'll also need an InfluxDB instance to store the fetched data. Make sure to configure
your InfluxDB connection details in the script before running it.

You will also need to obtain a token from the NOAA's API. This token should be placed in the HEADERS constant at the top
of the script.

## Usage

1. Set your API token in the `HEADERS` constant at the top of the script.

    ```python
    HEADERS = {
        "token": "your_api_token_here"
    }
    ```

2. Set your InfluxDB connection details in the constants at the top of the script:

   ```python
   
   INFLUXDB_HOST = '<your_host>'
   INFLUXDB_PORT = '<your_port>'
   INFLUXDB_USER = '<your_user>'
   INFLUXDB_PASSWORD = '<your_password>'
   INFLUXDB_DATABASE = '<your_database>'
   ```

3. Run the script from the command line:

    ```bash
    python climate_data_fetcher.py
    ```

   The script will start fetching climate data for all countries. Progress will be shown in the console.

## Rate Limiting

The script manages rate limiting based on the `MAX_REQUESTS_PER_SECOND` constant. By default, it is set to 5 requests
per second.

## Fetching Specific Date Ranges

The script fetches data for the latest available date for each country. If you want to fetch data for a specific date
range, modify the fetch_and_write_climate_data_to_influxdb function accordingly.

## Note

This is an unofficial script and is not affiliated with or endorsed by NOAA. Always check
the [NOAA's API terms of service](https://www.ncdc.noaa.gov/cdo-web/webservices/v2) before using the script.

## License

This project is licensed under the terms of the MIT license.
