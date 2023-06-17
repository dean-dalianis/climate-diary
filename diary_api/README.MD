# diary_api

The diary_api provides access to a range of climate-related data. It is built with Flask and Flask-RESTX and provides a
Swagger UI for easy interaction and testing.

The API connects to an InfluxDB database, fetches the data based on the specified conditions, and returns it in a
well-structured JSON format.

Currently, all endpoints are in the app.py file. They will be moved to separate files in the future.

## Swagger UI

The Swagger UI is available at `localhost:8000` endpoint. It provides a convenient way to interact with the API and test
it, as well as a documentation of the API endpoints.

## Features (so far)

- Fetch all climate data for a given country.
- Fetch climate data for a given country on a specific date.
- Fetch climate data for a given country within a specific date range.
- Fetch specific measurement data for a given country.
- Fetch specific measurement data for a given country on a specific date.
- Fetch specific measurement data for a given country within a specific date range.

## Running and Deployment

Please refer to the [README](../README.MD) file in the root directory of the project for instructions on how to run the
API and the accompanying services.