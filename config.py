"""
EV Auto Comp Sales Tracker - Configuration
Defines all competitor dealers, their inventory URLs, and scraping strategies.
"""

DEALERS = {
    "ev_auto": {
        "name": "EV Auto",
        "is_us": True,  # This is our dealership
        "sites": [
            {
                "url": "https://www.evauto.com/used-inventory/index.htm",
                "platform": "dealerinspire",
                "tesla_filter": "?make=Tesla",
                "rivian_filter": "?make=Rivian",
            }
        ],
    },
    "kentson": {
        "name": "Kentson Car Company",
        "is_us": False,
        "sites": [
            {
                "url": "https://www.kentsonbountiful.com/used-vehicles/",
                "platform": "dealersocket",
                "tesla_filter": "?make=Tesla",
                "rivian_filter": "?make=Rivian",
            },
            {
                "url": "https://www.kentsonamericanfork.com/used-vehicles/",
                "platform": "dealersocket",
                "tesla_filter": "?make=Tesla",
                "rivian_filter": "?make=Rivian",
            },
        ],
    },
    "recharged": {
        "name": "Recharged",
        "is_us": False,
        "sites": [
            {
                "url": "https://recharged.com/vehicles",
                "platform": "custom_recharged",
                "tesla_filter": "?makes=Tesla&count=200",
                "rivian_filter": "?makes=Rivian&count=200",
            }
        ],
    },
    "axio_ev": {
        "name": "Axio EV",
        "is_us": False,
        "sites": [
            {
                "url": "https://www.axioev.com/certified-inventory/index.htm",
                "platform": "dealerinspire",
                "tesla_filter": "?make=Tesla",
                "rivian_filter": "?make=Rivian",
            }
        ],
    },
    "electric_cars_hq": {
        "name": "Electric Cars HQ",
        "is_us": False,
        "sites": [
            {
                "url": "https://www.electriccarshq.com/used-inventory/index.htm",
                "platform": "dealerinspire",
                "tesla_filter": "?make=Tesla",
                "rivian_filter": "?make=Rivian",
            }
        ],
    },
    "mountain_auto_slc": {
        "name": "Mountain Auto SLC",
        "is_us": False,
        "sites": [
            {
                "url": "https://mountainautoslc.com/",
                "platform": "custom_mountain",
                "tesla_filter": "",
                "rivian_filter": "",
            }
        ],
    },
    "ever_cars": {
        "name": "Ever Cars",
        "is_us": False,
        "sites": [
            {
                "url": "https://www.evercars.com/cars",
                "platform": "custom_ever",
                "tesla_filter": "?make=Tesla",
                "rivian_filter": "?make=Rivian",
            }
        ],
    },
    "family_auto": {
        "name": "Family Auto",
        "is_us": False,
        "sites": [
            {
                "url": "https://www.familyautoslc.com/",
                "platform": "custom_family",
                "tesla_filter": "",
                "rivian_filter": "",
            }
        ],
    },
    "redline_auto": {
        "name": "Redline Auto",
        "is_us": False,
        "sites": [
            {
                "url": "https://drivecoolcars.com/",
                "platform": "custom_redline",
                "tesla_filter": "",
                "rivian_filter": "",
            }
        ],
    },
    "asay_auto": {
        "name": "Asay Auto",
        "is_us": False,
        "sites": [
            {
                "url": "https://asayauto.com/",
                "platform": "custom_asay",
                "tesla_filter": "",
                "rivian_filter": "",
            }
        ],
    },
}

# VIN regex pattern - standard 17-character VIN
VIN_PATTERN = r'\b[A-HJ-NPR-Z0-9]{17}\b'

# Tesla VINs start with 5YJ or 7SA
TESLA_VIN_PREFIXES = ['5YJ', '7SA', '7G2']

# Rivian VINs start with 7PD or 7FC
RIVIAN_VIN_PREFIXES = ['7PD', '7FC', '7PR']

# Slack config (set via environment variable)
SLACK_WEBHOOK_URL = ""  # Set via SLACK_WEBHOOK_URL env var
SLACK_CHANNEL = ""  # Set via SLACK_CHANNEL env var

# Data storage path
DATA_DIR = "data"
