import json
import os

DB_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config/db_config.json')
with open(DB_CONFIG_FILE, 'r') as file:
    config = json.load(file)
HOST = config['HOST']
PORT = config['PORT']
USERNAME = os.environ.get('DB_ADMIN_USER', 'admin')
PASSWORD = os.environ.get('DB_ADMIN_PASSWORD', 'changeme')
ORG = os.environ.get('DB_ORG', 'noaa')
BUCKET = os.environ.get('DB_BUCKET', 'noaa_gsom')

GSOY_DATA_DIR = 'files/gsoy_data'

FIELD_MAPPING = {
    # 'AWND': {
    #     'name': 'Average_Daily_Wind_Speed',
    #     'attributes': ['source_code']
    # },
    # 'CDSD': {
    #     'name': 'Cooling_Degree_Days_season-to-date',
    #     'attributes': ['source_code']
    # },
    'CLDD': {
        'name': 'Cooling_Degree_Days',
        'attributes': ['days_missing', 'source_code']
    },
    # 'DP01': {
    #     'name': 'Number_of_Days_with_at_least_0.254_mm_of_Precipitation',
    #     'attributes': ['source_code']
    # },
    # 'DP10': {
    #     'name': 'Number_of_Days_with_at_least_2.54_mm_of_Precipitation',
    #     'attributes': ['source_code']
    # },
    # 'DP1X': {
    #     'name': 'Number_of_Days_with_at_least_25.4_mm_of_Precipitation',
    #     'attributes': ['source_code']
    # },
    # 'DSND': {
    #     'name': 'Number_of_Days_with_Snow_Depth_at_least_25.4mm',
    #     'attributes': []
    # },
    'DSNW': {
        'name': 'Number_of_Days_with_Snowfall',
        'attributes': ['days_missing', 'source_code']
    },
    # 'DT00': {
    #     'name': 'Number_of_Days_with_Maximum_Temperature<=-17.8°C',
    #     'attributes': ['source_code']
    # },
    # 'DT32': {
    #     'name': 'Number_of_Days_with_Minimum_Temperature<=0°C',
    #     'attributes': ['source_code']
    # },
    # 'DX32': {
    #     'name': 'Number_of_Days_with_Maximum_Temperature<=0°C',
    #     'attributes': ['source_code']
    # },
    # 'DX70': {
    #     'name': 'Number_of_Days_with_Maximum_Temperature>=21.1°C',
    #     'attributes': ['source_code']
    # },
    # 'DX90': {
    #     'name': 'Number_of_Days_with_Maximum_Temperature>=32.2°C',
    #     'attributes': ['source_code']
    # },
    'DYFG': {
        'name': 'Number_of_Days_with_Fog',
        'attributes': []
    },
    'DYTS': {
        'name': 'Number_of_Days_with_Thunder',
        'attributes': []
    },
    'EMNT': {
        'name': 'Extreme_Minimum_Temperature',
        'attributes': ['source_code', 'date', 'more_than_once']
    },
    'EMSD': {
        'name': 'Highest_Daily_Snow_Depth',
        'attributes': ['measurement_flag', 'source_code', 'date', 'more_than_once']
    },
    'EMSN': {
        'name': 'Highest_Daily_Snowfall',
        'attributes': ['measurement_flag', 'source_code', 'date', 'more_than_once']
    },
    'EMXP': {
        'name': 'Extreme_Maximum_Precipitation',
        'attributes': ['measurement_flag', 'source_code', 'date', 'more_than_once']
    },
    'EMXT': {
        'name': 'Extreme_Maximum_Temperature',
        'attributes': ['source_code', 'date', 'more_than_once']
    },
    'EVAP': {
        'name': 'Total_Evaporation',
        'attributes': ['source_code']
    },
    # 'FZF0': {
    #     'name': 'Temperature_Value_of_First_Freeze_at_or_less_than_0°C_Aug-Dec',
    #     'attributes': ['source_code', 'date']
    # },
    # 'FZF1': {
    #     'name': 'Temperature_Value_of_First_Freeze_at_or_less_than_-2.2°C_Aug-Dec',
    #     'attributes': ['source_code', 'date']
    # },
    # 'FZF2': {
    #     'name': 'Temperature_Value_of_First_Freeze_at_or_less_than_-4.4°C_Aug-Dec',
    #     'attributes': ['source_code', 'date']
    # },
    # 'FZF3': {
    #     'name': 'Temperature_Value_of_First_Freeze_at_or_less_than_-6.7°C_Aug-Dec',
    #     'attributes': ['source_code', 'date']
    # },
    # 'FZF4': {
    #     'name': 'Temperature_Value_of_First_Freeze_at_or_less_than_-8.9°C_Aug-Dec',
    #     'attributes': ['source_code', 'date']
    # },
    # 'FZF5': {
    #     'name': 'Temperature_Value_of_First_Freeze_at_or_less_than_0°C_Jan-Jul',
    #     'attributes': ['source_code', 'date']
    # },
    # 'FZF6': {
    #     'name': 'Temperature_Value_of_First_Freeze_at_or_less_than_-2.2°C_Jan-Jul',
    #     'attributes': ['source_code', 'date']
    # },
    # 'FZF7': {
    #     'name': 'Temperature_Value_of_First_Freeze_at_or_less_than_-4.4°C_Jan-Jul',
    #     'attributes': ['source_code', 'date']
    # },
    # 'FZF8': {
    #     'name': 'Temperature_Value_of_First_Freeze_at_or_less_than_-6.7°C_Jan-Jul',
    #     'attributes': ['source_code', 'date']
    # },
    # 'FZF9': {
    #     'name': 'Temperature_Value_of_First_Freeze_at_or_less_than_-8.9°C_Jan-Jul',
    #     'attributes': ['source_code', 'date']
    # },
    # 'HDSD': {
    #     'name': 'Heating_Degree_Days_season_to_date',
    #     'attributes': ['source_code']
    # },
    'HTDD': {
        'name': 'Heating_Degree_Days',
        'attributes': ['days_missing', 'source_code']
    },
    # 'MNPN': {
    #     'name': 'Annual_Mean_Minimum_Temperature_of_evaporation_pan',
    #     'attributes': ['source_code']
    # },
    # 'MXPN': {
    #     'name': 'Annual_Mean_Maximum_Temperature_of_evaporation_pan',
    #     'attributes': ['source_code']
    # },
    'PRCP': {
        'name': 'Total_Precipitation',
        'attributes': ['measurement_flag', 'source_code']
    },
    'PSUN': {
        'name': 'Percent_of_Possible_Sunshine',
        'attributes': ['source_code']
    },
    'SNOW': {
        'name': 'Total_Snowfall',
        'attributes': ['measurement_flag', 'source_code']
    },
    'TAVG': {
        'name': 'Average_Temperature',
        'attributes': ['source_code']
    },
    'TMAX': {
        'name': 'Maximum_Temperature',
        'attributes': ['source_code']
    },
    'TMIN': {
        'name': 'Minimum_Temperature',
        'attributes': ['source_code']
    },
    'TSUN': {
        'name': 'Total_Sunshine_in_minutes',
        'attributes': ['days_missing', 'source_code']
    },
    # 'WDF1': {
    #     'name': 'Wind_Direction_for_Maximum_Wind_Speed_Fastest_1-Minute_WSF1',
    #     'attributes': ['source_code']
    # },
    # 'WDF2': {
    #     'name': 'Wind_Direction_for_Maximum_Wind_Speed_Fastest_2-Minute_WSF2',
    #     'attributes': ['source_code']
    # },
    # 'WDF5': {
    #     'name': 'Wind_Direction_for_Maximum_Wind_Speed_Fastest_5-Second_WSF5',
    #     'attributes': ['source_code']
    # },
    # 'WDFG': {
    #     'name': 'Wind_Direction_for_Peak_Wind_Gust',
    #     'attributes': ['source_code']
    # },
    # 'WDFI': {
    #     'name': 'Direction_of_Highest_Instantaneous_Wind_Speed',
    #     'attributes': ['days_missing', 'source_code']
    # },
    # 'WDFM': {
    #     'name': 'Wind_Direction_for_Maximum_Wind_Speed',
    #     'attributes': ['source_code']
    # },
    # 'WDMV': {
    #     'name': 'Total_annual_wind_movement_over_evaporation_pan',
    #     'attributes': ['source_code']
    # },
    # 'WSF1': {
    #     'name': 'Maximum_Wind_Speed_Fastest_1-minute',
    #     'attributes': ['source_code']
    # },
    # 'WSF2': {
    #     'name': 'Maximum_Wind_Speed_Fastest_2-minute',
    #     'attributes': ['source_code']
    # },
    # 'WSF5': {
    #     'name': 'Peak_Wind_Gust_Speed_Fastest_5-second',
    #     'attributes': ['source_code']
    # },
    # 'WSFG': {
    #     'name': 'Peak_Wind_Gust_Speed',
    #     'attributes': ['source_code']
    # },
    # 'WSFI': {
    #     'name': 'Highest_Instantaneous_Wind_Speed',
    #     'attributes': ['days_missing', 'source_code']
    # },
    # 'WSFM': {
    #     'name': 'Maximum_Wind_Speed',
    #     'attributes': ['source_code']
    # }
}

FIPS_MAPPING = {
    "AF": {"country_name": "Afghanistan", "country_iso": "AF"},
    "AX": {"country_name": "Aland Islands", "country_iso": "AX"},
    "AL": {"country_name": "Albania", "country_iso": "AL"},
    "AG": {"country_name": "Algeria", "country_iso": "DZ"},
    "AQ": {"country_name": "American Samoa", "country_iso": "AS"},
    "AN": {"country_name": "Andorra", "country_iso": "AD"},
    "AO": {"country_name": "Angola", "country_iso": "AO"},
    "AV": {"country_name": "Anguilla", "country_iso": "AI"},
    "AY": {"country_name": "Antarctica", "country_iso": "AQ"},
    "AC": {"country_name": "Antigua and Barbuda", "country_iso": "AG"},
    "AR": {"country_name": "Argentina", "country_iso": "AR"},
    "AM": {"country_name": "Armenia", "country_iso": "AM"},
    "AA": {"country_name": "Aruba", "country_iso": "AW"},
    "AS": {"country_name": "Australia", "country_iso": "AU"},
    "AU": {"country_name": "Austria", "country_iso": "AT"},
    "AJ": {"country_name": "Azerbaijan", "country_iso": "AZ"},
    "BF": {"country_name": "Bahamas", "country_iso": "BS"},
    "BA": {"country_name": "Bahrain", "country_iso": "BH"},
    "BG": {"country_name": "Bangladesh", "country_iso": "BD"},
    "BB": {"country_name": "Barbados", "country_iso": "BB"},
    "BO": {"country_name": "Belarus", "country_iso": "BY"},
    "BE": {"country_name": "Belgium", "country_iso": "BE"},
    "BH": {"country_name": "Belize", "country_iso": "BZ"},
    "BN": {"country_name": "Benin", "country_iso": "BJ"},
    "BD": {"country_name": "Bermuda", "country_iso": "BM"},
    "BT": {"country_name": "Bhutan", "country_iso": "BT"},
    "BL": {"country_name": "Bolivia (Plurinational State of)", "country_iso": "BO"},
    "BQ": {"country_name": "Bonaire, Sint Eustatius and Saba", "country_iso": "BQ"},
    "BK": {"country_name": "Bosnia and Herzegovina", "country_iso": "BA"},
    "BC": {"country_name": "Botswana", "country_iso": "BW"},
    "BV": {"country_name": "Bouvet Island", "country_iso": "BV"},
    "BR": {"country_name": "Brazil", "country_iso": "BR"},
    "IO": {"country_name": "British Indian Ocean Territory", "country_iso": "IO"},
    "BX": {"country_name": "Brunei Darussalam", "country_iso": "BN"},
    "BU": {"country_name": "Bulgaria", "country_iso": "BG"},
    "UV": {"country_name": "Burkina Faso", "country_iso": "BF"},
    "BY": {"country_name": "Burundi", "country_iso": "BI"},
    "CV": {"country_name": "Cabo Verde", "country_iso": "CV"},
    "CB": {"country_name": "Cambodia", "country_iso": "KH"},
    "CM": {"country_name": "Cameroon", "country_iso": "CM"},
    "CA": {"country_name": "Canada", "country_iso": "CA"},
    "CJ": {"country_name": "Cayman Islands", "country_iso": "KY"},
    "CT": {"country_name": "Central African Republic", "country_iso": "CF"},
    "CD": {"country_name": "Chad", "country_iso": "TD"},
    "CI": {"country_name": "Chile", "country_iso": "CL"},
    "CH": {"country_name": "China", "country_iso": "CN"},
    "KT": {"country_name": "Christmas Island", "country_iso": "CX"},
    "CK": {"country_name": "Cocos (Keeling) Islands", "country_iso": "CC"},
    "CO": {"country_name": "Colombia", "country_iso": "CO"},
    "CN": {"country_name": "Comoros", "country_iso": "KM"},
    "CF": {"country_name": "Congo", "country_iso": "CG"},
    "CG": {"country_name": "Congo (Democratic Republic of the)", "country_iso": "CD"},
    "CW": {"country_name": "Cook Islands", "country_iso": "CK"},
    "CS": {"country_name": "Costa Rica", "country_iso": "CR"},
    "IV": {"country_name": "Cote d’Ivoire", "country_iso": "CI"},
    "HR": {"country_name": "Croatia", "country_iso": "HR"},
    "CU": {"country_name": "Cuba", "country_iso": "CU"},
    "UC": {"country_name": "Curacao", "country_iso": "CW"},
    "CY": {"country_name": "Cyprus", "country_iso": "CY"},
    "EZ": {"country_name": "Czechia", "country_iso": "CZ"},
    "DA": {"country_name": "Denmark", "country_iso": "DK"},
    "DJ": {"country_name": "Djibouti", "country_iso": "DJ"},
    "DO": {"country_name": "Dominica", "country_iso": "DM"},
    "DR": {"country_name": "Dominican Republic", "country_iso": "DO"},
    "EC": {"country_name": "Ecuador", "country_iso": "EC"},
    "EG": {"country_name": "Egypt", "country_iso": "EG"},
    "ES": {"country_name": "El Salvador", "country_iso": "SV"},
    "EK": {"country_name": "Equatorial Guinea", "country_iso": "GQ"},
    "ER": {"country_name": "Eritrea", "country_iso": "ER"},
    "EN": {"country_name": "Estonia", "country_iso": "EE"},
    "ET": {"country_name": "Ethiopia", "country_iso": "ET"},
    "FK": {"country_name": "Falkland Islands (Malvinas)", "country_iso": "FK"},
    "FO": {"country_name": "Faroe Islands", "country_iso": "FO"},
    "FJ": {"country_name": "Fiji", "country_iso": "FJ"},
    "FI": {"country_name": "Finland", "country_iso": "FI"},
    "FR": {"country_name": "France", "country_iso": "FR"},
    "FG": {"country_name": "French Guiana", "country_iso": "GF"},
    "FP": {"country_name": "French Polynesia", "country_iso": "PF"},
    "FS": {"country_name": "French Southern Territories", "country_iso": "TF"},
    "GB": {"country_name": "Gabon", "country_iso": "GA"},
    "GA": {"country_name": "Gambia", "country_iso": "GM"},
    "GG": {"country_name": "Georgia", "country_iso": "GE"},
    "GM": {"country_name": "Germany", "country_iso": "DE"},
    "GH": {"country_name": "Ghana", "country_iso": "GH"},
    "GI": {"country_name": "Gibraltar", "country_iso": "GI"},
    "GR": {"country_name": "Greece", "country_iso": "GR"},
    "GL": {"country_name": "Greenland", "country_iso": "GL"},
    "GJ": {"country_name": "Grenada", "country_iso": "GD"},
    "GP": {"country_name": "Guadeloupe", "country_iso": "GP"},
    "GQ": {"country_name": "Guam", "country_iso": "GU"},
    "GT": {"country_name": "Guatemala", "country_iso": "GT"},
    "GK": {"country_name": "Guernsey", "country_iso": "GG"},
    "GV": {"country_name": "Guinea", "country_iso": "GN"},
    "PU": {"country_name": "Guinea-Bissau", "country_iso": "GW"},
    "GY": {"country_name": "Guyana", "country_iso": "GY"},
    "HA": {"country_name": "Haiti", "country_iso": "HT"},
    "HM": {"country_name": "Heard Island and McDonald Islands", "country_iso": "HM"},
    "VT": {"country_name": "Holy See", "country_iso": "VA"},
    "HO": {"country_name": "Honduras", "country_iso": "HN"},
    "HK": {"country_name": "Hong Kong", "country_iso": "HK"},
    "HU": {"country_name": "Hungary", "country_iso": "HU"},
    "IC": {"country_name": "Iceland", "country_iso": "IS"},
    "IN": {"country_name": "India", "country_iso": "IN"},
    "ID": {"country_name": "Indonesia", "country_iso": "ID"},
    "IR": {"country_name": "Iran (Islamic Republic of)", "country_iso": "IR"},
    "IZ": {"country_name": "Iraq", "country_iso": "IQ"},
    "EI": {"country_name": "Ireland", "country_iso": "IE"},
    "IM": {"country_name": "Isle of Man", "country_iso": "IM"},
    "IS": {"country_name": "Israel", "country_iso": "IL"},
    "IT": {"country_name": "Italy", "country_iso": "IT"},
    "JM": {"country_name": "Jamaica", "country_iso": "JM"},
    "JA": {"country_name": "Japan", "country_iso": "JP"},
    "JE": {"country_name": "Jersey", "country_iso": "JE"},
    "JO": {"country_name": "Jordan", "country_iso": "JO"},
    "KZ": {"country_name": "Kazakhstan", "country_iso": "KZ"},
    "KE": {"country_name": "Kenya", "country_iso": "KE"},
    "KR": {"country_name": "Kiribati", "country_iso": "KI"},
    "KN": {"country_name": "Korea (Democratic People’s Republic of)", "country_iso": "KP"},
    "KS": {"country_name": "Korea (Republic of)", "country_iso": "KR"},
    "KU": {"country_name": "Kuwait", "country_iso": "KW"},
    "KG": {"country_name": "Kyrgyzstan", "country_iso": "KG"},
    "LA": {"country_name": "Lao People’s Democratic Republic", "country_iso": "LA"},
    "LG": {"country_name": "Latvia", "country_iso": "LV"},
    "LE": {"country_name": "Lebanon", "country_iso": "LB"},
    "LT": {"country_name": "Lesotho", "country_iso": "LS"},
    "LI": {"country_name": "Liberia", "country_iso": "LR"},
    "LY": {"country_name": "Libya", "country_iso": "LY"},
    "LS": {"country_name": "Liechtenstein", "country_iso": "LI"},
    "LH": {"country_name": "Lithuania", "country_iso": "LT"},
    "LU": {"country_name": "Luxembourg", "country_iso": "LU"},
    "MC": {"country_name": "Macao", "country_iso": "MO"},
    "MK": {"country_name": "North Macedonia", "country_iso": "MK"},
    "MA": {"country_name": "Madagascar", "country_iso": "MG"},
    "MI": {"country_name": "Malawi", "country_iso": "MW"},
    "MY": {"country_name": "Malaysia", "country_iso": "MY"},
    "MV": {"country_name": "Maldives", "country_iso": "MV"},
    "ML": {"country_name": "Mali", "country_iso": "ML"},
    "MT": {"country_name": "Malta", "country_iso": "MT"},
    "RM": {"country_name": "Marshall Islands", "country_iso": "MH"},
    "MB": {"country_name": "Martinique", "country_iso": "MQ"},
    "MR": {"country_name": "Mauritania", "country_iso": "MR"},
    "MP": {"country_name": "Mauritius", "country_iso": "MU"},
    "MQ": {"country_name": "Midway Atoll", "country_iso": "UM"},
    "MF": {"country_name": "Mayotte", "country_iso": "YT"},
    "MX": {"country_name": "Mexico", "country_iso": "MX"},
    "FM": {"country_name": "Micronesia (Federated States of)", "country_iso": "FM"},
    "MD": {"country_name": "Moldova (Republic of)", "country_iso": "MD"},
    "MN": {"country_name": "Monaco", "country_iso": "MC"},
    "MG": {"country_name": "Mongolia", "country_iso": "MN"},
    "MJ": {"country_name": "Montenegro", "country_iso": "ME"},
    "MH": {"country_name": "Montserrat", "country_iso": "MS"},
    "MO": {"country_name": "Morocco", "country_iso": "MA"},
    "MZ": {"country_name": "Mozambique", "country_iso": "MZ"},
    "BM": {"country_name": "Myanmar", "country_iso": "MM"},
    "WA": {"country_name": "Namibia", "country_iso": "NA"},
    "NR": {"country_name": "Nauru", "country_iso": "NR"},
    "NP": {"country_name": "Nepal", "country_iso": "NP"},
    "NL": {"country_name": "Netherlands", "country_iso": "NL"},
    "NC": {"country_name": "New Caledonia", "country_iso": "NC"},
    "NZ": {"country_name": "New Zealand", "country_iso": "NZ"},
    "NU": {"country_name": "Nicaragua", "country_iso": "NI"},
    "NG": {"country_name": "Niger", "country_iso": "NE"},
    "NI": {"country_name": "Nigeria", "country_iso": "NG"},
    "NE": {"country_name": "Niue", "country_iso": "NU"},
    "NF": {"country_name": "Norfolk Island", "country_iso": "NF"},
    "CQ": {"country_name": "Northern Mariana Islands", "country_iso": "MP"},
    "NO": {"country_name": "Norway", "country_iso": "NO"},
    "MU": {"country_name": "Oman", "country_iso": "OM"},
    "PK": {"country_name": "Pakistan", "country_iso": "PK"},
    "PS": {"country_name": "Palau", "country_iso": "PW"},
    "WE": {"country_name": "Palestine, State of", "country_iso": "PS"},
    "PM": {"country_name": "Panama", "country_iso": "PA"},
    "PP": {"country_name": "Papua New Guinea", "country_iso": "PG"},
    "PA": {"country_name": "Paraguay", "country_iso": "PY"},
    "PE": {"country_name": "Peru", "country_iso": "PE"},
    "RP": {"country_name": "Philippines", "country_iso": "PH"},
    "PC": {"country_name": "Pitcairn", "country_iso": "PN"},
    "PL": {"country_name": "Poland", "country_iso": "PL"},
    "PO": {"country_name": "Portugal", "country_iso": "PT"},
    "RQ": {"country_name": "Puerto Rico", "country_iso": "PR"},
    "QA": {"country_name": "Qatar", "country_iso": "QA"},
    "RE": {"country_name": "Reunion", "country_iso": "RE"},
    "RO": {"country_name": "Romania", "country_iso": "RO"},
    "RS": {"country_name": "Russian Federation", "country_iso": "RU"},
    "RW": {"country_name": "Rwanda", "country_iso": "RW"},
    "TB": {"country_name": "Saint Barthelemy", "country_iso": "BL"},
    "SH": {"country_name": "Saint Helena, Ascension and Tristan da Cunha", "country_iso": "SH"},
    "SC": {"country_name": "Saint Kitts and Nevis", "country_iso": "KN"},
    "ST": {"country_name": "Saint Lucia", "country_iso": "LC"},
    "RN": {"country_name": "Saint Martin", "country_iso": "MF"},
    "SB": {"country_name": "Saint Pierre and Miquelon", "country_iso": "PM"},
    "VC": {"country_name": "Saint Vincent and the Grenadines", "country_iso": "VC"},
    "WS": {"country_name": "Samoa", "country_iso": "WS"},
    "SM": {"country_name": "San Marino", "country_iso": "SM"},
    "TP": {"country_name": "Sao Tome and Principe", "country_iso": "ST"},
    "SA": {"country_name": "Saudi Arabia", "country_iso": "SA"},
    "SG": {"country_name": "Senegal", "country_iso": "SN"},
    "RI": {"country_name": "Serbia", "country_iso": "RS"},
    "SE": {"country_name": "Seychelles", "country_iso": "SC"},
    "SL": {"country_name": "Sierra Leone", "country_iso": "SL"},
    "SN": {"country_name": "Singapore", "country_iso": "SG"},
    "NN": {"country_name": "Sint Maarten", "country_iso": "SX"},
    "LO": {"country_name": "Slovakia", "country_iso": "SK"},
    "SI": {"country_name": "Slovenia", "country_iso": "SI"},
    "BP": {"country_name": "Solomon Islands", "country_iso": "SB"},
    "SO": {"country_name": "Somalia", "country_iso": "SO"},
    "SF": {"country_name": "South Africa", "country_iso": "ZA"},
    "SX": {"country_name": "South Georgia and the South Sandwich Islands", "country_iso": "GS"},
    "OD": {"country_name": "South Sudan", "country_iso": "SS"},
    "SP": {"country_name": "Spain", "country_iso": "ES"},
    "CE": {"country_name": "Sri Lanka", "country_iso": "LK"},
    "SU": {"country_name": "Sudan", "country_iso": "SD"},
    "NS": {"country_name": "Suriname", "country_iso": "SR"},
    "SV": {"country_name": "Svalbard and Jan Mayen", "country_iso": "SJ"},
    "WZ": {"country_name": "Eswatini", "country_iso": "SZ"},
    "SW": {"country_name": "Sweden", "country_iso": "SE"},
    "SZ": {"country_name": "Switzerland", "country_iso": "CH"},
    "SY": {"country_name": "Syrian Arab Republic", "country_iso": "SY"},
    "TW": {"country_name": "Taiwan (Province of China)", "country_iso": "TW"},
    "TI": {"country_name": "Tajikistan", "country_iso": "TJ"},
    "TZ": {"country_name": "Tanzania, United Republic of", "country_iso": "TZ"},
    "TH": {"country_name": "Thailand", "country_iso": "TH"},
    "TT": {"country_name": "Timor-Leste", "country_iso": "TL"},
    "TO": {"country_name": "Togo", "country_iso": "TG"},
    "TL": {"country_name": "Tokelau", "country_iso": "TK"},
    "TN": {"country_name": "Tonga", "country_iso": "TO"},
    "TD": {"country_name": "Trinidad and Tobago", "country_iso": "TT"},
    "TS": {"country_name": "Tunisia", "country_iso": "TN"},
    "TU": {"country_name": "Turkey", "country_iso": "TR"},
    "TX": {"country_name": "Turkmenistan", "country_iso": "TM"},
    "TK": {"country_name": "Turks and Caicos Islands", "country_iso": "TC"},
    "TV": {"country_name": "Tuvalu", "country_iso": "TV"},
    "UG": {"country_name": "Uganda", "country_iso": "UG"},
    "UP": {"country_name": "Ukraine", "country_iso": "UA"},
    "AE": {"country_name": "United Arab Emirates", "country_iso": "AE"},
    "UK": {"country_name": "United Kingdom of Great Britain and Northern Ireland", "country_iso": "GB"},
    "US": {"country_name": "United States of America", "country_iso": "US"},
    "UM": {"country_name": "United States Minor Outlying Islands", "country_iso": "UM"},
    "UY": {"country_name": "Uruguay", "country_iso": "UY"},
    "UZ": {"country_name": "Uzbekistan", "country_iso": "UZ"},
    "NH": {"country_name": "Vanuatu", "country_iso": "VU"},
    "VE": {"country_name": "Venezuela (Bolivarian Republic of)", "country_iso": "VE"},
    "VM": {"country_name": "Vietnam", "country_iso": "VN"},
    "VI": {"country_name": "Virgin Islands (British)", "country_iso": "VG"},
    "VQ": {"country_name": "Virgin Islands (U.S.)", "country_iso": "VI"},
    "WF": {"country_name": "Wallis and Futuna", "country_iso": "WF"},
    "WI": {"country_name": "Western Sahara", "country_iso": "EH"},
    "YM": {"country_name": "Yemen", "country_iso": "YE"},
    "ZA": {"country_name": "Zambia", "country_iso": "ZM"},
    "ZI": {"country_name": "Zimbabwe", "country_iso": "ZW"}
}
