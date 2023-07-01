# Diary API

A simple API for fetching data from the Climate Diary database.

## Swagger UI

The Swagger UI is available at `localhost:8000` endpoint. It provides a convenient way to interact with the API and test
it, as well as a documentation of the API endpoints.

## Base URL

The base URL for all API endpoints is `/`.

## Endpoints

### Fetch Analyzed Climate Data

- Endpoint: `/diary/analysis/data`
- Method: GET
- Description: Fetch analyzed climate data based on specified conditions

#### Parameters

- `country_id` (string, default: 'AL'): A country ID
- `measurement` (string, default: 'Average_Temperature_decadal_average'): A measurement name
- `date` (string, default: null): A specific date (YYYY-MM-DD)
- `start_date` (string, default: '2016-01-01'): Start date of a range (YYYY-MM-DD)
- `end_date` (string, default: '2022-12-31'): End date of a range (YYYY-MM-DD)
- `X-Fields` (header, string, format: mask): An optional fields mask

#### Responses

- 200: Climate data matching the specified conditions. [Array of Analysis_Measurement objects](#definitions)
- 404: No data found for the specified conditions.

### Fetch Climate Data

- Endpoint: `/diary/gsom/data`
- Method: GET
- Description: Fetch climate data based on specified conditions

#### Parameters

- `country_id` (string, default: 'AL'): A country ID
- `measurement` (string, default: 'Average_Temperature'): A measurement name
- `date` (string, default: null): A specific date (YYYY-MM-DD)
- `start_date` (string, default: '2016-01-01'): Start date of a range (YYYY-MM-DD)
- `end_date` (string, default: '2022-12-31'): End date of a range (YYYY-MM-DD)
- `X-Fields` (header, string, format: mask): An optional fields mask

#### Responses

- 200: Climate data matching the specified conditions. [Array of Gsom_Measurement objects](#definitions)
- 404: No data found for the specified conditions.

### Fetch a List of All Available Countries

- Endpoint: `/diary/other/countries`
- Method: GET
- Description: Fetch a list of all available countries

#### Responses

- 200: List of countries with available data.
- 404: No countries found.

### Fetch the Earliest Timestamp

- Endpoint: `/diary/other/earliest`
- Method: GET
- Description: Fetch the earliest timestamp for a country or all countries

#### Responses

- 200: Earliest timestamp for all countries.
- 404: No timestamp found.

### Fetch the Latest Timestamp

- Endpoint: `/diary/other/latest`
- Method: GET
- Description: Fetch the latest timestamp for a country or all countries

#### Responses

- 200: Latest timestamp for all countries.
- 404: No timestamp found.

### Fetch a List of Available Measurements

- Endpoint: `/diary/other/measurements/`
- Method: GET
- Description: Fetch a list of available measurements for the specified country or all countries if no country ID is
  specified

#### Parameters

- `country_id` (string): A country ID

#### Responses

- 200: List of available measurements for the specified country or all countries.
- 404: No measurements found for this country ID or no countries found.

### Fetch a List of Available Measurements (with Country ID)

- Endpoint: `/diary/other/measurements/{country_id}`
- Method: GET
- Description: Fetch a list of available measurements for the specified country or all countries if no country ID is
  specified

#### Parameters

- `country_id` (path, string, required): A country ID

#### Responses

- 200: List of available measurements for the specified country or all countries.
- 404: No measurements found for this country ID or no countries found.

### Fetch Climate Data Trends

- Endpoint: `/diary/trends/data`
- Method: GET
- Description: Fetch climate data trends based on specified conditions

#### Parameters

- `country_id` (string, default: 'AL'): A country ID
- `measurement` (string, default: 'Average_Temperature_trend'): A measurement name
- `X-Fields` (header, string, format: mask): An optional fields mask

#### Responses

- 200: Climate data trends matching the specified conditions. [Array of Trends_Measurement objects](#definitions)
- 404: No data found for the specified conditions.

## Definitions

### Analysis_Measurement

- `measurement` (string): Measurement name
- `country_name` (string): Country name
- `value` (number): Measurement value
- `time` (string, format: date-time): Timestamp

### Gsom_Measurement

- `measurement` (string): Measurement name
- `country_name` (string): Country name
- `value` (number): Measurement value
- `time` (string, format: date-time): Timestamp

### Trends_Measurement

- `measurement` (string): Measurement name
- `country_name` (string): Country name
- `value` (number): Trend value
- `time` (number): Trend value

## Available measurements

The API supports querying the following measurements as created by `gsom_fetcher`:

- `GSOY_MEASUREMENTS`:
    - Average_Temperature
    - Maximum_Temperature
    - Minimum_Temperature
    - Extreme_Maximum_Temperature
    - Extreme_Minimum_Temperature
    - Precipitation
    - Highest_Daily_Total_Of_Precipitation
    - Highest_Daily_Snow_Depth

- `TRENDS_MEASUREMENTS`:
    - Average_Temperature_trend
    - Extreme_Maximum_Temperature_trend
    - Extreme_Minimum_Temperature_yearly_average
    - Highest_Daily_Snow_Depth_trend
    - Highest_Daily_Total_Of_Precipitation_trend
    - Maximum_Temperature_trend
    - Minimum_Temperature_trend
    - Precipitation_trend

- `ANALYSIS_MEASUREMENTS`:
    - Average_Temperature_decadal_average
    - Average_Temperature_dod_change
    - Average_Temperature_monthly_average
    - Average_Temperature_yearly_average
    - Average_Temperature_yoy_change
    - Extreme_Maximum_Temperature_decadal_average
    - Extreme_Maximum_Temperature_dod_change
    - Extreme_Maximum_Temperature_monthly_average
    - Extreme_Maximum_Temperature_yearly_average
    - Extreme_Maximum_Temperature_yoy_change
    - Extreme_Minimum_Temperature_decadal_average
    - Extreme_Minimum_Temperature_dod_change
    - Extreme_Minimum_Temperature_monthly_average
    - Extreme_Minimum_Temperature_yearly_average
    - Extreme_Minimum_Temperature_yoy_change
    - Highest_Daily_Snow_Depth_decadal_average
    - Highest_Daily_Snow_Depth_dod_change
    - Highest_Daily_Snow_Depth_monthly_average
    - Highest_Daily_Snow_Depth_yearly_average
    - Highest_Daily_Snow_Depth_yoy_change
    - Highest_Daily_Total_Of_Precipitation_decadal_average
    - Highest_Daily_Total_Of_Precipitation_dod_change
    - Highest_Daily_Total_Of_Precipitation_monthly_average
    - Highest_Daily_Total_Of_Precipitation_yearly_average
    - Highest_Daily_Total_Of_Precipitation_yoy_change
    - Maximum_Temperature_decadal_average
    - Maximum_Temperature_dod_change
    - Maximum_Temperature_monthly_average
    - Maximum_Temperature_yearly_average
    - Maximum_Temperature_yoy_change
    - Minimum_Temperature_decadal_average
    - Minimum_Temperature_dod_change
    - Minimum_Temperature_monthly_average
    - Minimum_Temperature_yearly_average
    - Minimum_Temperature_yoy_change
    - Precipitation_decadal_average
    - Precipitation_dod_change
    - Precipitation_monthly_average
    - Precipitation_yearly_average
    - Precipitation_yoy_change

- `METADATA_MEASUREMENT`: metadata

## Running and Deployment

Please refer to the [README](../README.MD) file in the root directory of the project for instructions on how to run the
API and the accompanying services.