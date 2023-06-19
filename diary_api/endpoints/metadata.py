from flask_restx import Api, Resource

from influx.metadata import fetch_last_update_time

from logging_config import logger


def initialize_routes(api: Api):
    metadata_namespace = api.namespace('diary/metadata', description='Metadata')

    @metadata_namespace.route('/last_update_time')
    class LastUpdateTime(Resource):
        @metadata_namespace.doc('get_latest_timestamp',
                                responses={200: 'Latest update timestamp.',
                                           404: 'No timestamp found'})
        def get(self):
            """
            Fetch the latest timestamp for a country or all countries
            """
            logger.info('Fetching latest update timestamp.')
            timestamp = fetch_last_update_time()
            logger.info(f'Fetched latest update timestamp: {timestamp}.')
            if timestamp:
                return timestamp, 200
            else:
                return {"message": "No latest update timestamp found."}, 404
