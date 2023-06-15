FROM python:3.9-slim

# Install cron package
RUN apt-get update && apt-get install -y cron

# Set the working directory
WORKDIR /gsom_fetcher

# Copy the Python script(s) and requirements.txt to the container
COPY noaa_gsom_fetcher/ /gsom_fetcher/

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the cron job file to the container
COPY ./docker/gsom_fetcher/cronjob /etc/cron.d/cronjob

# Give execution rights to the cron job
RUN chmod 0644 /etc/cron.d/cronjob

# Apply the cron job
RUN crontab /etc/cron.d/cronjob

# Run cron
CMD python3 /gsom_fetcher/noaa_gsom_fetcher.py && cron -f