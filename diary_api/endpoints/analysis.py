from flask import request
from flask_restx import Api, Resource, fields
from influx.analysis import fetch_data
from logging_config import logger


def initialize_routes(api: Api):
    analysis_namespace = api.namespace('diary/analysis', description='analyzed climate data for countries')

    analysis_measurement = api.model('Analysis_Measurement', {
        'measurement': fields.String(required=True, description='Measurement name'),
        'country_name': fields.String(required=True, description='Country name'),
        'value': fields.Float(required=True, description='Measurement value'),
        'time': fields.DateTime(required=True, description='Timestamp', dt_format='iso8601'),
    })

    @analysis_namespace.route('/data')
    class ClimateData(Resource):
        @analysis_namespace.doc('fetch_analyzed_climate_data',
                                params={
                                    'country_id': {'description': 'A country id', 'type': 'string', 'default': 'AL'},
                                    'measurement': {'description': 'A measurement name', 'type': 'string',
                                                    'default': 'Average_Temperature_decadal_average'},
                                    'date': {'description': 'A specific date (YYYY-MM-DD)', 'type': 'string',
                                             'default': None},
                                    'start_date': {'description': 'Start date of a range (YYYY-MM-DD)',
                                                   'type': 'string', 'default': '2016-01-01'},
                                    'end_date': {'description': 'End date of a range (YYYY-MM-DD)', 'type': 'string',
                                                 'default': '2022-12-31'}},
                                responses={200: 'Climate data matching the specified conditions.',
                                           404: 'No data found for the specified conditions.'},
                                return_model=analysis_measurement)
        @analysis_namespace.marshal_list_with(analysis_measurement)
        def get(self):
            """
            Fetch analyzed climate data based on specified conditions
            """
            country_id = request.args.get('country_id')
            measurement = request.args.get('measurement')
            date = request.args.get('date')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            if date and (start_date or end_date):
                return {"message": "You cannot set both 'date' and 'start_date'/'end_date' parameters."}, 400

            logger.info(
                f'Fetching analyzed climate data for country ID: {country_id}, measurement: {measurement}, date: {date}, '
                f'start date: {start_date}, end date: {end_date}.')
            data = fetch_data(country_id, measurement, date, start_date, end_date)
            logger.info(f'Fetched {len(data) if data is not None else ""} analyzed climate data records.')

            if data:
                return data, 200
            else:
                return {
                           "message": "No analyzed climate data found for the specified conditions. Are you sure you are using the correct API endpoint?"}, 404
