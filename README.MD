# NOAA GSOM fetcher

This repository contains multiple projects that

- fetch, analyze, and write climate data to an InfluxDb database for world's countries (easily extendable to all
  countries, but due to resource constraints, only European countries are currently supported)
- provide an API to access the data
- provide a web application to visualize the data
- provide a Grafana instance to visualize the data

Each project has its own README file with more detailed documentation.

## Data Types and Attribute Decoding

**gsom_fetcher** fetches various types of climate data from the NOAA API.

The data types, their attributes, and the full names of the measurements can be found below.

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

**not all attributes are stored in the database*

## Station Information

In addition to climate data, the script also retrieves details for each station. The station details include the
following information:

- Elevation: The elevation of the station.
- Latitude: The latitude of the station.
- Longitude: The longitude of the station.
- Name: The name of the station.
- Data Coverage: The percentage of data coverage for the station.
- ID: The ID of the station.

**not all station details are stored in the database*

## Data Analysis

The data analysis is done in the gsom_fetcher project. The analysis produces the following results:

- monthly averages
- yearly averages
- decadal averages
- year-over-year changes
- decade-over-decade changes
- trends

*More details about the analysis can be found in the gsom_fetcher README.*

## Docker

The project uses Docker to run all the services. The services are defined in the `docker-compose.yml`.

### Services

The services included in the stack are:

1. **influxDB**: A time series database for storing metrics and time-based data.
2. **grafana**: A platform for visualizing and analyzing metrics with customizable dashboards and plugins.
3. **gsom_fetcher**: A custom Python script for fetching climate data using the NOAA GSOM API.
4. **frontend**: The React app for the diary.
5. **backent**: The API for the diary app.
6. **nginx**: A web server for serving the frontend and backend.

### Running the Stack

To run the stack, follow these steps:

1. Clone this repository to your local system.

2. Create an `.env` file in the root directory of the project and add the following environment variables to it:

    ```
    DB_ADMIN_PASSWORD=<admin_password>
    DB_NAME=noaa_gsom
    NOAA_TOKEN_1=<noaa_token_1>
    NOAA_TOKEN_2=<noaa_token_2>
    NOAA_TOKEN_3=<noaa_token_3>
    NOAA_TOKEN_4=<noaa_token_4>
    NOAA_TOKEN_5=<noaa_token_5>
    ```

3. Run the following command to start the containers:

    ```bash
    docker compose --env-file ./.env -f ./docker-compose.yml up --remove-orphans --build
    ```

   If you need to start containers selectively (e.g. the influxdb & grafana or any other combination):
   ```bash
   docker compose --env-file ./.env -f ./docker-compose.yml up --remove-orphans --build influxdb grafana
    ```

   If you need to clean-up docker deployments:

    ```bash
    docker-compose --env-file ./.env -f ./docker-compose.yml down --volumes --remove-orphans
    ```

   And manually remove the created directories in your local host machine:
    - containers
    - gsom_fetcher/container/
    - diary_api/container/

4. After the containers are up and running, you can access the following services:

    - influxDB: [http://localhost:8086](http://localhost:8086)
    - grafana: [http://localhost:3000](http://localhost:3000)
    - frontend: [http://localhost:8081](http://localhost:8081)
    - backend: [http://localhost:8000](http://localhost:8000)

5. To stop the containers, run the following command:

    ```bash
    docker-compose down
    ```

### Configuration

The Docker configuration files for the services are stored in their respective directories:

- **influxdb**: `provisioning/influxdb/influxdb.conf`
- **grafana**: `grafana/grafana.ini`
- **gsom_fetcher**: `gsom_fetcher/Dockerfile`
- **frontend**: `diary/Dockerfile`
- **backend**: `diary_api/Dockerfile`
- **nginx**: `nginx/Dockerfile`

You can modify these files to change the configuration of the services.

### Docker Volumes

- **grafana** mounts
    - `grafana/counteiner/grafana_data` directory as a volume for data persistence.
    - `grafana/provisioning` directory as a volume for provisioning.
- **influxdb** mounts
    - `containers/influxdb_data/` directory as a volume for data persistence.
- **gsom_fetcher** mounts
    - `gsom_fetcher/container/log/` directory as a volume for logging.
- **backend** mounts
    - `diary_api/container/log/` directory as a volume for logging.
- **nginx** mounts
    - `nginx/container/log/` directory as a volume for logging.
    - `nginx/container/nginx.conf` file as a volume for configuration.
    - `nginx/container/conf.d/` directory as a volume for configuration.

## License

This project is licensed under the terms of the MIT license.

___

## In Progress && To-Do

- [ ] **frontend**:
    - [x] Added ([react-simple-maps](https://www.react-simple-maps.io/)
    - [x] Currently, deployed using docker-compose
    - [ ] Implement a proper frontend
- [x] **backend**:
    - [x] Created a simple API with Flask and Flask-RESTful
    - [x] Root endpoint loads the Swaaaggggeerrr UI
    - [x] Currently, deployed using docker-compose
    - [x] Add more endpoints according to the frontend needs
    - [x] Add endpoint for the metadata measurement (only includes the last udpate date)
- [ ] **nginx**:
    - [x] Add nginx to the docker-compose stack
    - [x] Serve the backend with nginx
    - [x] Serve the frontend with nginx
    - [ ] Remove the backend serve after the frontend is ready
- [ ] **minor file restructure**:
    - [ ] Move the provisioning file for influx outside from `provisioning/influxdb` `influxdb` directory
    - [ ] Move the `containers/influxdb_data/` directory to the `influxdb/container/influxdb_data/` directory
- [x] **grafana**
    - [x] **datasource provisioning**: current datasource provisioning doesn't create the password (it's empty)
    - [x] **dashboard provisioning**: add provisioning for the dashboard itself
- [ ] **More data:**
    - [ ] co2 historic data
    - [ ] co2 live data
    - [ ] temperature live data
    - [ ] ice melting historic data
    - [ ] ice melting live data
    - [ ] socioeconomic data
- [ ] **Cloud Configuration**: configure a cloud environment to run the containers