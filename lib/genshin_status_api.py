import requests
from io import BytesIO
import json
import aiohttp

API_URL_BASE = "http://genshin.api/"

async def get_user_data(uid:int):
    endpoint_url = f"{API_URL_BASE}status/uid/{uid}"
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(endpoint_url) as response:
            resp = await response.json()
    return resp

async def api_connect_generate_image(data, image_type:int):
    endpoint_url = f"{API_URL_BASE}buildimage/genshinstat/{image_type}/"
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint_url, json=data) as response:
            file = BytesIO(await response.read())
            return file
        
async def api_connect_profile_image(data):
    endpoint_url = f"{API_URL_BASE}buildimage/profile/" 
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint_url, json=data) as response:
            file = BytesIO(await response.read())
            return file
        