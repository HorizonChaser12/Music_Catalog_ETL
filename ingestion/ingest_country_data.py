import json
import logging
import requests
import os
# Configure logging to print to console
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# Set the logger level to DEBUG so that it includes all logs from this script
logger.setLevel(logging.DEBUG)


# needs to be parameterized, so that it can get data based on the matching Country Data
countryId = "f19249a4-0b66-4ae9-be67-7d9f9ea9069f"
country_data = None
file_path = "/opt/project/data/"


def get_country_data():
    try:
        country_data = requests.get(f"http://food-delivery-api:4000/v1/country/{countryId}")
        # country_data = requests.get(f"http://localhost:4000/v1/country/{countryId}")
        if country_data.status_code == 200:
            logger.info("API fetched successfully")
            file_name = f"{file_path}{countryId}.json"
            logger.info(f"Writing data to: {file_name}")  
            with open(file_name, "w") as f:
                f.write(json.dumps(country_data.json(), indent=2))
                f.close()
            logger.info(f"Data has been written to {file_name}. Ingestion Completed!") 
        elif country_data.status_code == 204:
            logger.debug(f"failed to fetch the contents from the API:{country_data.status_code}")
            country_data.raise_for_status()         
              
    except Exception as e:
        if countryId is None:
            logger.info("countryId is empty, please check and retry the API request")
            raise
        else:
            logger.error(f"Failed to fetch country data: {e}")
            raise
    