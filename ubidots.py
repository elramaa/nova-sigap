from dotenv import load_dotenv
import os
import requests
import json
load_dotenv()

UBIDOTS_HEADER  = {
    "Content-Type": "application/json",
    "X-Auth-Token": os.getenv('UBIDOTS_TOKEN')
}
UBIDOTS_DEVICE = os.getenv("UBIDOTS_DEVICE")
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE}"

def send_to_ubidots(var, data):
    response = requests.post(url=UBIDOTS_URL, data=json.dumps({var: data}), headers=UBIDOTS_HEADER)
    print(response.text)

def get_var_ubidots(var):
    url = "https://industrial.api.ubidots.com/api/v2.0/variables/"
    print(url)
    response = requests.get(url=url, headers=UBIDOTS_HEADER)
    print(response.text)


