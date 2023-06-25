# gsom_fetcher

This is a Python application that fetches, analyzes, and writes climate data to a database for European countries (due
to resource constraints). The data is fetched from the National Oceanic and Atmospheric Administration (NOAA) and
includes information on various climate attributes such as temperature, precipitation, wind speed, etc.

The application contains multi-threading to perform concurrent analysis of data for each country.

## Modules Description

- **gsom_fetcher.py**: The main module that starts the fetching, analysis, and writing processes.

- **analysis.py**: Contains the functions for data analysis.

- **config.py**: Configuration file where variables like the minimum start year, max workers, etc. are defined.

- **influx.py**: Defines the functions for interacting with the InfluxDB database.

- **logging_config.py**: Contains the configuration for logging.

- **noaa_requests.py**: Defines the functions for making requests to the NOAA API.

- **util.py**: Contains utility functions for manipulating dates and checking run conditions.

## Functions Description

The application contains several functions that perform specific tasks. The descriptions of the main functions are as
follows:

- **fetch_gsom_data_from_noaa_and_write_to_database()**: Fetches climate data from NOAA for each country and writes it
  to the database.

- **analyze_countries()**: Analyzes the data for each country in parallel using multiple threads.

- **fetch_measurements_from_db()**: Fetches all measurements from the database for a country.

- **fetch_countries()**: Fetches a list of all countries from the NOAA API.


## Rate Limiting

The script manages rate limiting based on the `MAX_REQUESTS_PER_SECOND` constant. By default, it is set to 5 requests
per second, which is the limit of NOAA API. Also, the API has a limit of 10.000 requests per token per day.

## Available measurements

`gsom_fetcher` creates the following measurements in the database:

- `DEFAULT_MEASUREMENTS`:
    - Average_Temperature
    - Maximum_Temperature
    - Minimum_Temperature
    - Extreme_Maximum_Temperature
    - Extreme_Minimum_Temperature
    - Precipitation
    - Highest_Daily_Total_Of_Precipitation
    - Highest_Daily_Snow_Depth

- `TRENDS_MEASUREMENTS`:
    - Average_Temperature_trend
    - Extreme_Maximum_Temperature_trend
    - Extreme_Minimum_Temperature_yearly_average
    - Highest_Daily_Snow_Depth_trend
    - Highest_Daily_Total_Of_Precipitation_trend
    - Maximum_Temperature_trend
    - Minimum_Temperature_trend
    - Precipitation_trend

- `ANALYSIS_MEASUREMENTS`:
    - Average_Temperature_decadal_average
    - Average_Temperature_dod_change
    - Average_Temperature_monthly_average
    - Average_Temperature_yearly_average
    - Average_Temperature_yoy_change
    - Extreme_Maximum_Temperature_decadal_average
    - Extreme_Maximum_Temperature_dod_change
    - Extreme_Maximum_Temperature_monthly_average
    - Extreme_Maximum_Temperature_yearly_average
    - Extreme_Maximum_Temperature_yoy_change
    - Extreme_Minimum_Temperature_decadal_average
    - Extreme_Minimum_Temperature_dod_change
    - Extreme_Minimum_Temperature_monthly_average
    - Extreme_Minimum_Temperature_yearly_average
    - Extreme_Minimum_Temperature_yoy_change
    - Highest_Daily_Snow_Depth_decadal_average
    - Highest_Daily_Snow_Depth_dod_change
    - Highest_Daily_Snow_Depth_monthly_average
    - Highest_Daily_Snow_Depth_yearly_average
    - Highest_Daily_Snow_Depth_yoy_change
    - Highest_Daily_Total_Of_Precipitation_decadal_average
    - Highest_Daily_Total_Of_Precipitation_dod_change
    - Highest_Daily_Total_Of_Precipitation_monthly_average
    - Highest_Daily_Total_Of_Precipitation_yearly_average
    - Highest_Daily_Total_Of_Precipitation_yoy_change
    - Maximum_Temperature_decadal_average
    - Maximum_Temperature_dod_change
    - Maximum_Temperature_monthly_average
    - Maximum_Temperature_yearly_average
    - Maximum_Temperature_yoy_change
    - Minimum_Temperature_decadal_average
    - Minimum_Temperature_dod_change
    - Minimum_Temperature_monthly_average
    - Minimum_Temperature_yearly_average
    - Minimum_Temperature_yoy_change
    - Precipitation_decadal_average
    - Precipitation_dod_change
    - Precipitation_monthly_average
    - Precipitation_yearly_average
    - Precipitation_yoy_change

- `METADATA_MEASUREMENT`: metadata

## Running and Deployment

Please refer to the [README](../README.MD) file in the root directory of the project for instructions on how to run the
API and the accompanying services.
