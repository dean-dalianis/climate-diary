import logging
import os
from logging.handlers import TimedRotatingFileHandler

os.makedirs('log', exist_ok=True)  # Create the log directory if it doesn't exist

# Set up log rotation
log_filename = 'log/diaryapi.log'
log_handler = TimedRotatingFileHandler(log_filename, when='D', interval=1, backupCount=7)
log_handler.suffix = "%Y-%m-%d"
log_handler.setLevel(logging.INFO)

# Set up console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Set up logging format
log_format = '%(asctime)s %(levelname)s %(message)s'
log_formatter = logging.Formatter(log_format)
log_handler.setFormatter(log_formatter)
console_handler.setFormatter(log_formatter)

# Set up root logger
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
