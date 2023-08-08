import requests
from io import BytesIO
import json

API_URL_BASE = "http://172.25.0.3/"

def get_user_data(uid:int):
    endpoint_url = f"{API_URL_BASE}status/uid/{uid}/"
    return json.loads(requests.get(endpoint_url).content.decode())

def api_connect_generate_image(data, image_type:int):
    endpoint_url = f"{API_URL_BASE}buildimage/genshinstat/{image_type}/"
    response = requests.post(endpoint_url, json=data)
    if response:
        return BytesIO(response.content)
    else:
        print("No image data found in the response.")

def api_connect_profile_image(data):
    endpoint_url = f"{API_URL_BASE}buildimage/profile/"
    response = requests.post(endpoint_url, json=data)
    if response:
        return BytesIO(response.content)
    else:
        print("No image data found in the response.")