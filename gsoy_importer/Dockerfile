FROM python:3.10-alpine

# Install cron package
RUN apt-get update && apt-get install -y cron && apt-get install -y procps

# Set the working directory
WORKDIR /gsoy_importer

# Copy the Python script(s) and requirements.txt to the container
COPY ./ /gsoy_importer/

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the cron job file to the container
COPY ./cronjob /etc/cron.d/cronjob

# Give execution rights to the cron job
RUN chmod 0644 /etc/cron.d/cronjob

# Apply the cron job
RUN crontab /etc/cron.d/cronjob

# Run
CMD python3 /gsoy_importer/importer.py && cron -f