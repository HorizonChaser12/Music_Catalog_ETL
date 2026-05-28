from matplotlib.font_manager import json_dump
import requests 
import json

resp = requests.post("http://localhost:4000/v1/user/register", json={"username": "","email": "","password": ""})
print(resp.status_code)
print(resp.headers.get("content-type"))
print(resp.text[:400])

# data = resp.json()
# print(data)

# url = "http://localhost:4000/user/register"


# data = {
    
# }

# response = requests.post(url, json=data)

# print(response.status_code)
# print(response.json())