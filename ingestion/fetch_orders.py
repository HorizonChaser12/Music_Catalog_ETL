import requests
import json
from datetime import datetime

url="https://jsonplaceholder.typicode.com/users"
response = requests.get(url)
data = response.json() 
current_date = datetime.now().strftime("%Y_%m_%d")
file_path = f"data/raw/orders/orders_{current_date}.json"

with open(file_path,"w") as file:
    json.dump(data, file)

