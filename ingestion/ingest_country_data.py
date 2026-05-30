import json
import logging
import requests

# Configure logging to print to console
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)



# needs to be parameterized, so that it can get data based on the matching Country Data
countryId = "6bbf8a3e-0777-4e93-9de1-a28d2d160f9a"
country_data = None
file_path = "data/raw/"

try:
    country_data = requests.get(f"http://localhost:4000/v1/country/{countryId}")
    if country_data.status_code == 200:
        logger.info("API fetched successfully")
        file_name = f"{file_path}{countryId}.json"
        logger.info(f"Writing data to: {file_name}")  
        with open( file_name, "w") as f:
            f.write(json.dumps(country_data.json(), indent=2))
            f.close()
        logger.info(f"Data has been written to {file_name}. Ingestion Completed!")    
          
except Exception as e:
    if countryId is None:
        logger.info("countryId is empty, please check and retry the API request")
    else:
        logger.error(f"Failed to fetch country data: {e}")
       