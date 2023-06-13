# NOAA GSOM fetcher

Climate Data Fetcher fetches and stores historical climate data from the Global Summary of the Month (GSOM) dataset in
NOAA's Climate Data Online (CDO) API. It fetches data such as daily maximum and minimum temperatures, average
temperature, precipitation, snowfall, and other metrics for a selected subset of countries*. The script manages API
request rate limiting and handles possible API response errors.

**Due to resource limits, this analysis is currently performed only for countries in the European continent*

## Data Types and Attribute Decoding

The script fetches various types of climate data, each of which may have associated attributes. These attributes provide
additional information about the data. For example, the number of days a particular measurement was missing, any
measurement or quality flags, and source codes.

Below are the data types the script fetches and the associated attributes:

```json
  "ATTRIBUTES": {
"TAVG": ["days_missing", "source_code"],
"TMAX": ["days_missing", "measurement_flag", "quality_flag", "source_code"],
"TMIN": ["days_missing", "measurement_flag", "quality_flag", "source_code"],
"EMXT": ["days_missing", "daily_dataset_source_code", "day", "more_than_once"],
"EMNT": ["days_missing", "daily_dataset_source_code", "day", "more_than_once"],
"PRCP": ["days_missing", "measurement_flag", "quality_flag", "source_code"],
"EMXP": ["days_missing", "daily_dataset_flag", "daily_dataset_source_code", "day", "more_than_once"],
"EMSD": ["days_missing", "daily_dataset_flag", "daily_dataset_source_code", "day", "more_than_once"]
},
"MEASUREMENT_NAMES": {
"TAVG": "Average_Temperature",
"TMAX": "Maximum_Temperature",
"TMIN": "Minimum_Temperature",
"EMXT": "Extreme_Maximum_Temperature",
"EMNT": "Extreme_Minimum_Temperature",
"PRCP": "Precipitation",
"EMXP": "Highest_Daily_Total_Of_Precipitation",
"EMSD": "Highest_Daily_Snow_Depth"
}
```

The decode_attributes function in the script takes care of decoding these attributes from the API response and storing
them in the InfluxDB along with the corresponding data.

For any new data type that you want to fetch, ensure that you add the associated attributes to the ATTRIBUTES dictionary
in the script.

Please note that the 'source_code' attribute, if present, is excluded during the attribute decoding process.

## Station Information

In addition to climate data, the script also retrieves details for each station. The station details include the
following information:

- Elevation: The elevation of the station.
- Latitude: The latitude of the station.
- Longitude: The longitude of the station.
- Name: The name of the station.
- Data Coverage: The percentage of data coverage for the station.
- ID: The ID of the station.

## Rate Limiting

The script manages rate limiting based on the `MAX_REQUESTS_PER_SECOND` constant. By default, it is set to 5 requests
per second, which is the limit of NOAA API. Also, the API has a limit of 10.000 requests per token per day.

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
    DB_NAME=noaa_gsom
    NOAA_TOKEN_1=<noaa_token_1>
    NOAA_TOKEN_2=<noaa_token_2>
    NOAA_TOKEN_3=<noaa_token_3>
    NOAA_TOKEN_4=<noaa_token_4>
    NOAA_TOKEN_5=<noaa_token_5>
    ```

3. Build the Docker images and start the containers by running the following command in the terminal:

    ```bash
    docker compose --env-file .\docker\.env -f ./docker/docker-compose.yml up --remove-orphans --build
    ```

   If you need to clean-up docker deployments:

    ```bash
    docker-compose --env-file .\docker\.env -f .\docker\docker-compose.yml down --volumes --remove-orphans
    ```

   And manually remove the created directories in your local host machine.

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
- There is an issue with Grafana datasource provisioning. The password for the `Basic Auth Details` and the DB user
  should be set manually.

## License

This project is licensed under the terms of the MIT license.


---

# To-Do list

List of stuff to do within the following week (12 - 17 / 06):

1. **Fetch Socioeconomic Data**: expand the functionality of the script to fetch socioeconomic data (both static and
   time-variable).
2. **Live Temperature Data Feed**: integrate a live temperature data feed into the script.
3. **Cloud Configuration**: configure a cloud environment to run the containers
4. **Grafana datasource provisioning**: current datasource provisioning doesn't create the password (it's empty)
5. **Grafana dashboard provisioning**: add provisioning for the dashboard itself
6. **Nginx server on docker**
7. **Flask backend**
8. **React frontend // otherwise plain html/css/js**
9. **D3/Chart.js dashboard implementation**: showcase temperature change, in an animation-like manner, in a worldmap

Update and cross-out at will.
