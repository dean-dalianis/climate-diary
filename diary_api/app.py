from flask import Flask
from flask_restx import Api, Resource, fields

from influx import fetch_all_data

app = Flask(__name__)
api = Api(app, version='1.0', title='Climate Data API', description='A climate data API')

ns = api.namespace('country_data', description='Climate operations')

measurement = api.model('Measurement', {
    'table': fields.String(required=True, description='Measurement name'),
    'value': fields.Float(required=True, description='Measurement value'),
    'country_name': fields.String(required=True, description='Country name'),
    'station': fields.String(required=True, description='Station'),
    'latitude': fields.Float(required=True, description='Latitude'),
    'longitude': fields.Float(required=True, description='Longitude'),
    'time': fields.DateTime(required=True, description='Timestamp', dt_format='iso8601'),
})


@ns.route('/<country_id>')
class GetCountryData(Resource):
    @ns.doc('get_country_data')
    @ns.marshal_with(measurement)
    def get(self, country_id):
        """
        Fetch data for a country

        :param str country_id: The country ID to fetch the climate data for.
        :return: A list of records based on the specified conditions or a message if no data is found.
        :rtype: list[dict] or dict
        """
        data = fetch_all_data(country_id)
        if data:
            return data, 200
        else:
            return {"message": "No data found for this country ID."}, 404


@ns.route('/date/<country_id>/<date>')
class GetCountryDataByDate(Resource):
    @ns.doc('get_country_data_by_date')
    @ns.marshal_with(measurement)
    def get(self, country_id, date):
        """
        Fetch data for a country for a specific date

        :param str country_id: The country ID to fetch the climate data for.
        :param str date: The specific date to fetch the data for. Format: 'YYYY-MM-DD'.
        :return: A list of records based on the specified conditions or a message if no data is found.
        :rtype: list[dict] or dict
        """
        data = fetch_all_data(country_id, date=date)
        if data:
            return data, 200
        else:
            return {"message": "No data found for this country ID on this date."}, 404


@ns.route('/range/<country_id>/<start_date>/<end_date>')
class GetCountryDataByRange(Resource):
    @ns.doc('get_country_data_by_range')
    @ns.marshal_with(measurement)
    def get(self, country_id, start_date, end_date):
        """Fetch data for a country for a specific date range"""
        data = fetch_all_data(country_id, start_date=start_date, end_date=end_date)
        if data:
            return data, 200
        else:
            return {"message": "No data found for this country ID in this date range."}, 404


@ns.route('/measurement/<country_id>/<measurement_name>')
class GetCountryDataByMeasurement(Resource):
    @ns.doc('get_country_data_by_measurement')
    @ns.marshal_with(measurement)
    def get(self, country_id, measurement_name):
        """Fetch data for a country for a specific measurement"""
        data = fetch_all_data(country_id, table_name=measurement_name)
        if data:
            return data, 200
        else:
            return {"message": "No data found for this country ID in this measurement."}, 404


@ns.route('/date_measurement/<country_id>/<measurement_name>/<date>')
class GetCountryDataByDateAndMeasurement(Resource):
    @ns.doc('get_country_data_by_date_and_measurement')
    @ns.marshal_with(measurement)
    def get(self, country_id, measurement_name, date):
        """Fetch data for a country for a specific date and measurement"""
        data = fetch_all_data(country_id, table_name=measurement_name, date=date)
        if data:
            return data, 200
        else:
            return {"message": "No data found for this country ID on this date in this measurement."}, 404


@ns.route('/range_measurement/<country_id>/<measurement_name>/<start_date>/<end_date>')
class GetCountryDataByRangeAndMeasurement(Resource):
    @ns.doc('get_country_data_by_range_and_measurement')
    @ns.marshal_with(measurement)
    def get(self, country_id, measurement_name, start_date, end_date):
        """Fetch data for a country for a specific date range and measurement"""
        data = fetch_all_data(country_id, table_name=measurement_name, start_date=start_date, end_date=end_date)
        if data:
            return data, 200
        else:
            return {"message": "No data found for this country ID in this date range in this measurement."}, 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
