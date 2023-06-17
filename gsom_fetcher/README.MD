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

- **fetch_stations()**: Fetches all weather stations for a specified country.

- **fetch_countries()**: Fetches a list of all countries from the NOAA API.

- **fetch_european_countries()**: Fetches a list of European countries from the NOAA API.

- **decode_attributes()**: Decodes the attributes string for a specified datatype.

## Rate Limiting

The script manages rate limiting based on the `MAX_REQUESTS_PER_SECOND` constant. By default, it is set to 5 requests
per second, which is the limit of NOAA API. Also, the API has a limit of 10.000 requests per token per day.

## License

This project is licensed under the terms of the MIT license.

## Running and Deployment

Please refer to the [README](../README.MD) file in the root directory of the project for instructions on how to run the
API and the accompanying services.