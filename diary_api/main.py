from flask import Flask
from flask_restx import Api

from endpoints.analysis import initialize_routes as initialize_analysis_routes
from endpoints.gsom import initialize_routes as initialize_gsom_routes
from endpoints.metadata import initialize_routes as initialize_metadata_routes
from endpoints.other import initialize_routes as initialize_other_routes
from endpoints.trends import initialize_routes as initialize_trends_routes


def create_app():
    app = Flask(__name__)
    api = Api(
        app,
        version='1.0',
        title='Diary API',
        description='A simple API for fetching data from the Climate Diary database.',
    )

    initialize_gsom_routes(api)
    initialize_other_routes(api)
    initialize_analysis_routes(api)
    initialize_trends_routes(api)
    initialize_metadata_routes(api)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # Set the host to '0.0.0.0' to make your server publicly available
