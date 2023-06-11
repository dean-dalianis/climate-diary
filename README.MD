# NOAA GSOM fetcher

Climate Data Fetcher fetches and stores historical climate data from the Global Summary of the Month (GSOM) dataset in
NOAA's Climate Data Online (CDO) API. It fetches data such as daily maximum and minimum temperatures, average
temperature, precipitation, snowfall, and other metrics for all available countries. The script manages API request rate
limiting and handles possible API response errors.

## Data Types and Attribute Decoding

The script fetches various types of climate data, each of which may have associated attributes. These attributes provide
additional information about the data. For example, the number of days a particular measurement was missing, any
measurement or quality flags, and source codes.

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

The decode_attributes function in the script takes care of decoding these attributes from the API response and storing
them in the InfluxDB along with the corresponding data.

For any new data type that you want to fetch, ensure that you add the associated attributes to the ATTRIBUTES dictionary
in the script.

Please note that the 'source_code' attribute, if present, is excluded during the attribute decoding process.

## Rate Limiting

The script manages rate limiting based on the `MAX_REQUESTS_PER_SECOND` constant. By default, it is set to 5 requests
per second.

## Note

This is an unofficial script and is not affiliated with or endorsed by NOAA. Always check
the [NOAA's API terms of service](https://www.ncdc.noaa.gov/cdo-web/webservices/v2) before using the script.

# Climate Monitoring Stack Using Docker

This project provides a Docker Compose configuration for setting up a monitoring stack with InfluxDB, Grafana, and a
custom climate data fetcher script for periodically fetching data from the NOAA GSOM dataset.

## Services

The services included in the stack are:

1. **InfluxDB**: A time series database for storing metrics and time-based data.
2. **Grafana**: A platform for visualizing and analyzing metrics with customizable dashboards and plugins.
3. **Climate Data Fetcher**: A custom Python script for fetching climate data using the NOAA GSOM API.

## Setup

To set up the monitoring stack with the climate data fetcher, follow these steps:

1. Clone this repository to your local system.

2. Create an `.env` file in the same directory as the `docker-compose.yml` file. Set the following environment variables
   in the `.env` file with your desired values:

    ```
    INFLUXDB_ADMIN_PASSWORD=<admin_password>
    NOAA_TOKEN=<noaa_token>
    BATCHSIZE=2 (optional -- default: 10)
    ```

3. Build the Docker images and start the containers by running the following command in the terminal:

    ```bash
    docker compose -f ./docker/docker-compose.yml up --remove-orphans --build
    ```

4. After the containers are up and running, you can access the following services:

    - InfluxDB: [http://localhost:8086](http://localhost:8086)
    - Grafana: [http://localhost:3000](http://localhost:3000)

5. To stop the containers, run the following command:

    ```bash
    docker-compose down
    ```

## Configuration

The configuration files for the services are stored in their respective directories:

- **InfluxDB**: `./docker/influxdb/influxdb.conf`
- **Grafana**: `./docker/grafana/grafana.ini`
- **Climate Data Fetcher**: `./docker/climate_data/Dockerfile`

Remember to edit these configuration files according to your needs.

## Additional Notes

- The InfluxDB container is initialized using the `init-influxdb.sh` script, which creates the necessary databases and
  users. The passwords for the users are set in the `.env` file.
- The Grafana container mounts the `grafana_data/` directory as a volume to persist data such as dashboards and
  configuration.
- The InfluxDB container mounts the `influxdb_data/` directory as a volume for data persistence.
- The climate data fetcher script container (`climate-data`) mounts the `docker/climate_data/log/` directory as a volume
  for logging.

## License

This project is licensed under the terms of the MIT license.
