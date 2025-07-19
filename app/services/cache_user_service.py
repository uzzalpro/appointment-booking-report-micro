import json
from utils.redis_client import redis_client

def get_user_info(user_id: int):
    key = f"user:{user_id}"
    user_data = redis_client.get(key)
    if user_data:
        return json.loads(user_data)
    return None
