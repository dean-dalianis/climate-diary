from flask import Flask, g
from flask_restx import Api
from influxdb_client import InfluxDBClient

from config import HOST, PORT, ORG, TOKEN
from endpoints.gsoy import initialize_routes as initialize_gsoy_routes
from endpoints.other import initialize_routes as initialize_other_routes


def create_app():
    app = Flask(__name__)
    api = Api(
        app,
        version='1.0',
        title='Diary API',
        description='A simple API for fetching data from the Climate Diary database.',
    )

    initialize_gsoy_routes(api)
    initialize_other_routes(api)

    @app.before_request
    def before_request():
        g.db = InfluxDBClient(
            url=f'http://{HOST}:{PORT}',
            token=TOKEN,
            org=ORG,
            enable_gzip=True
        )
        g.query_api = g.db.query_api()

    @app.teardown_appcontext
    def close_db_client(error=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # Set the host to '0.0.0.0' to make your server publicly available
