import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config/config.json')
with open(CONFIG_FILE, 'r') as file:
    config = json.load(file)

DEFAULT_MEASUREMENTS = config['DEFAULT_MEASUREMENTS']
ANALYSIS_MEASUREMENTS = config['ANALYSIS_MEASUREMENTS']
TRENDS_MEASUREMENTS = config['TRENDS_MEASUREMENTS']
METADATA_MEASUREMENT = config['METADATA_MEASUREMENT']

DB_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config/db_config.json')
with open(DB_CONFIG_FILE, 'r') as file:
    config = json.load(file)
HOST = config['HOST']
PORT = config['PORT']
BATCHSIZE = config['BATCHSIZE']

DB_NAME = os.environ.get('DB_NAME', 'noaa_gsom')
USERNAME = os.environ.get('DB_ADMIN_USER', 'admin')
PASSWORD = os.environ.get('DB_ADMIN_PASSWORD', 'changeme')
