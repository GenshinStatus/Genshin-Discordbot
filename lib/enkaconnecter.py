import aiohttp
from lib.yamlutil import yaml
import redis
import json

pool = redis.ConnectionPool(host="redis")
redis_obj = redis.StrictRedis(connection_pool=pool)

async def get_data(uid: str) -> dict:
    """APIからデータを取得しdictとして返却します

    Args:
        uid (str): UID

    Returns:
        dict: APIから取得したjsonをdictに変換したもの
    """
    if redis_obj.keys(uid):
        resp = json.loads(redis_obj.get(uid))
    else:
        url = f"https://enka.network/api/uid/{uid}"
        async with aiohttp.ClientSession(raise_for_status=True, headers={"User-Agent": "Genshin-Discordbot/1.6.7 (Linux; Ubuntu22.04; discord:CinnamonSea2073.zip#2073)"}) as session:
            async with session.get(url) as response:
                resp = await response.json()
                redis_obj.set(uid, json.dumps(resp))
                redis_obj.expire(uid, 300)
    return resp