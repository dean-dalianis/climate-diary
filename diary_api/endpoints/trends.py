from flask import request
from flask_restx import Api, Resource, fields
from influx.trends import fetch_data
from logging_config import logger


def initialize_routes(api: Api):
    trends_namespace = api.namespace('diary/trends', description='analyzed climate data for countries')

    trend_measurement = api.model('Trends_Measurement', {
        'measurement': fields.String(required=True, description='Measurement name'),
        'country_id': fields.String(required=True, description='Country ID'),
        'country_name': fields.String(required=True, description='Country name'),
        'slope': fields.Float(required=True, description='Measurement value'),
        'intercept': fields.Float(required=True, description='Measurement value'),
    })

    @trends_namespace.route('/data')
    class ClimateData(Resource):
        @trends_namespace.doc('fetch_climate_data_trends',
                              params={
                                  'country_id': {'description': 'A country id', 'type': 'string', 'default': 'AL'},
                                  'measurement': {'description': 'A measurement name', 'type': 'string',
                                                  'default': 'Average_Temperature_trend'}},
                              responses={200: 'Climate data trends matching the specified conditions.',
                                         404: 'No data found for the specified conditions.'},
                              return_model=trend_measurement)
        @trends_namespace.marshal_list_with(trend_measurement)
        def get(self):
            """
            Fetch climate data trends based on specified conditions
            """
            country_id = request.args.get('country_id')
            measurement = request.args.get('measurement')

            logger.info(
                f'Fetching climate data trends for country ID: {country_id}, measurement: {measurement}')
            data = fetch_data(country_id, measurement)
            logger.info(f'Fetched {len(data) if data is not None else ""} climate data trends records.')

            if data:
                return data, 200
            else:
                return {
                           "message": "No climate data trends found for the specified conditions. Are you sure you are using the correct API endpoint?"}, 404
