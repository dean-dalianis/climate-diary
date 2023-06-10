#!/bin/bash
set -e

influx -username 'admin' -password "${INFLUXDB_ADMIN_PASSWORD}" -execute 'CREATE DATABASE climate'
influx -username 'admin' -password "${INFLUXDB_ADMIN_PASSWORD}" -execute "CREATE USER climate WITH PASSWORD '${CLIMATE_PASSWORD}'"
influx -username 'admin' -password "${INFLUXDB_ADMIN_PASSWORD}" -execute 'GRANT ALL ON climate TO climate'
