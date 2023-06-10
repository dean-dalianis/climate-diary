FROM python:3.8-slim

# Install cron package
RUN apt-get update && apt-get install -y cron

# Set the working directory
WORKDIR /app

# Copy the Python script and requirements.txt to the container
COPY ../../noaa_gsom_fetcher/noaa_gsom_fetcher.py /app/noaa_gsom_fetcher.py
COPY ../../noaa_gsom_fetcher/requirements.txt /app/requirements.txt

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the cron job file to the container
COPY ./docker/climate_data/cronjob /etc/cron.d/cronjob

# Give execution rights to the cron job
RUN chmod 0644 /etc/cron.d/cronjob

# Apply the cron job
RUN crontab /etc/cron.d/cronjob

# Create the log file
RUN touch /var/log/cron.log

# Run cron and tail the log file
CMD python3 /app/noaa_gsom_fetcher.py && cron

