from flask_restx import Api, Resource

from influx.other import fetch_country_list, fetch_latest_timestamp, fetch_earliest_timestamp, \
    fetch_available_measurements, fetch_minimum_temperature, fetch_maximum_temperature

from logging_config import logger


def initialize_routes(api: Api):
    other_namespace = api.namespace('diary/other', description='Basic info about the data')

    @other_namespace.route('/countries')
    class CountryList(Resource):
        @other_namespace.doc('list_countries',
                             responses={200: 'List of countries with available data.',
                                        404: 'No countries found.'})
        def get(self):
            """
            Fetch a list of all available countries
            """
            logger.info('Fetching country list.')
            data = fetch_country_list()
            logger.info(f'Fetched {len(data)} countries.')
            if data:
                return data, 200
            else:
                return {"message": "No countries found."}, 404

    @other_namespace.route('/latest')
    class LatestTimestamp(Resource):
        @other_namespace.doc('get_latest_timestamp',
                             responses={200: 'Latest timestamp for all countries.',
                                        404: 'No timestamp found'})
        def get(self):
            """
            Fetch the latest timestamp for a country or all countries
            """
            logger.info('Fetching latest timestamp.')
            timestamp = fetch_latest_timestamp()
            logger.info(f'Fetched latest timestamp.')
            if timestamp:
                return timestamp, 200
            else:
                return {"message": "No latest timestamp found."}, 404

    @other_namespace.route('/earliest')
    class EarliestTimestamp(Resource):
        @other_namespace.doc('get_earliest_timestamp',
                             responses={200: 'Earliest timestamp for all countries.',
                                        404: 'No timestamp found'})
        def get(self):
            """
            Fetch the earliest timestamp for a country or all countries
            """
            logger.info('Fetching earliest timestamp.')
            timestamp = fetch_earliest_timestamp()
            logger.info(f'Fetched earliest timestamp.')
            if timestamp:
                return timestamp, 200
            else:
                return {"message": "No earliest timestamp found."}, 404

    @other_namespace.route('/measurements/', defaults={'country_iso': None})
    @other_namespace.route('/measurements/<string:country_iso>')
    class MeasurementsList(Resource):
        @other_namespace.doc('list_measurements',
                             params={
                                 'country_iso': {'description': 'A country iso', 'type': 'string', 'default': 'US'}},
                             responses={
                                 200: 'List of available measurements for the specified country or all countries.',
                                 404: 'No measurements found for this country iso or no countries found.'})
        def get(self, country_iso):
            """
            Fetch a list of available measurements for the specified country or all countries if no country iso is specified
            """
            logger.info(f'Fetching available measurements for country iso: {country_iso}.')
            timestamp = fetch_available_measurements(country_iso)
            logger.info(f'Fetched available measurements.')
            if timestamp:
                return timestamp, 200
            else:
                return {"message": "No measurements found for this country iso."}, 404

    @other_namespace.route('/temperature/minimum/<string:measurement>')
    class MinimumTemperature(Resource):
        @other_namespace.doc('get_minimum_temperature',
                             params={'measurement': {'description': 'A measurement name', 'type': 'string',
                                                     'default': 'Average_Temperature'}},
                             responses={
                                 200: 'The minimum temperature across all countries for the specified measurement.',
                                 404: 'No minimum temperature found for this measurement.'})
        def get(self, measurement):
            """
            Fetch the minimum temperature across all countries for the specified measurement
            """
            logger.debug(f'Fetching minimum temperature for measurement: {measurement}.')
            temperature = fetch_minimum_temperature(measurement)
            logger.debug(f'Fetched minimum temperature.')
            if temperature:
                return temperature, 200
            else:
                return {"message": "No minimum temperature found for this measurement."}, 404

    @other_namespace.route('/temperature/maximum/<string:measurement>')
    class MaximumTemperature(Resource):
        @other_namespace.doc('get_maximum_temperature',
                             params={'measurement': {'description': 'A measurement name', 'type': 'string',
                                                     'default': 'Average_Temperature'}},
                             responses={
                                 200: 'The maximum temperature across all countries for the specified measurement.',
                                 404: 'No maximum temperature found for this measurement.'})
        def get(self, measurement):
            """
            Fetch the minimum temperature across all countries for the specified measurement
            """
            if 'temperature' not in measurement.lower():
                return {'message': 'The measurement must be of type temperature.'}, 400

            logger.debug(f'Fetching maximum temperature for measurement: {measurement}.')
            temperature = fetch_maximum_temperature(measurement)
            logger.debug(f'Fetched maximum temperature.')
            if temperature:
                return temperature, 200
            else:
                return {"message": "No maximum temperature found for this measurement."}, 404
