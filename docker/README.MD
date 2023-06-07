# Grafana and InfluxDB Docker Compose Configuration

This repository provides Docker Compose configurations for setting up Grafana and InfluxDB on your system.

## Prerequisites

To use the Docker Compose configurations in this repository, you need to have the following installed on your system:

- Docker
- Docker Compose

## Getting Started

To get started with Grafana and InfluxDB, follow these steps:

1. Configure InfluxDB:

    - Follow the instructions in [here](https://blog.anoff.io/2020-12-run-influx-on-raspi-docker-compose/) set up
      InfluxDB using Docker Compose. Make sure to create the necessary directories, configure the InfluxDB and Telegraf
      files, and set up the required environment variables. Also, make sure to create an init script for climate data:
      ```bash
      CREATE DATABASE climate WITH DURATION INF
      CREATE USER climate WITH PASSWORD '<climateUSERpassword>'
      GRANT WRITE ON climate to climate```

2. Start Grafana and InfluxDB using Docker Compose:

   ```bash
   docker-compose up -d
   ```

3. Access Grafana:
    - Open your web browser and go to http://localhost:3000 to access the Grafana web interface.
    - Log in using the default credentials (username: admin, password: admin). You can change these credentials later in
      the Grafana UI.