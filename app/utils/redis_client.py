import redis

redis_client = redis.Redis(
    host='redis',  # or 'localhost' if not using Docker
    port=6379,
    decode_responses=True  # so you don't get byte strings
)
