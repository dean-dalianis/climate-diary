import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config/config.json')
with open(CONFIG_FILE, 'r') as file:
    config = json.load(file)

MIN_START_YEAR = config["MIN_START_YEAR"]
DATATYPE_ID = config["DATATYPE_ID"]
EU_CONTINENT_FIPS = config["EU_CONTINENT_FIPS"]
ATTRIBUTES = config["ATTRIBUTES"]
MEASUREMENT_NAMES = config["MEASUREMENT_NAMES"]
MAX_WORKERS = config["MAX_WORKERS"]

EXCLUDED_ATTRIBUTES = ['source_code', 'daily_dataset_measurement_source_code', 'daily_dataset_flag', 'measurement_flag',
                       'quality_flag']

DB_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config/db_config.json')
with open(DB_CONFIG_FILE, 'r') as file:
    config = json.load(file)
HOST = config['HOST']
PORT = config['PORT']
BATCHSIZE = config['BATCHSIZE']

DB_NAME = os.environ.get('DB_NAME', 'noaa_gsom')
USERNAME = os.environ.get('DB_ADMIN_USER', 'admin')
PASSWORD = os.environ.get('DB_ADMIN_PASSWORD', 'changeme')
