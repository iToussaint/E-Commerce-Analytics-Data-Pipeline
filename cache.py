import json
import os

import redis

TOP_PRODUCTS_KEY = "top_products"

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)


def get_top_products():
    """Return the cached top products, or None if they are not cached."""
    cached = redis_client.get(TOP_PRODUCTS_KEY)
    return json.loads(cached) if cached else None


def save_top_products(products):
    redis_client.set(TOP_PRODUCTS_KEY, json.dumps(products))


def clear_top_products():
    redis_client.delete(TOP_PRODUCTS_KEY)
