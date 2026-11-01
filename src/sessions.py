"""User session and shopping cart data stored in MongoDB."""

import os
from datetime import UTC, datetime

from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
sessions = client["ecommerce"]["sessions"]


def save_session(customer_id):
    """Create the customer's session if needed and mark it as active now."""
    sessions.update_one(
        {"customer_id": customer_id},
        {
            "$set": {"last_active": datetime.now(UTC)},
            "$setOnInsert": {"cart": []},
        },
        upsert=True,
    )


def add_to_cart(customer_id, product_id, quantity):
    # If the product is already in the cart, increase its quantity.
    result = sessions.update_one(
        {"customer_id": customer_id, "cart.product_id": product_id},
        {"$inc": {"cart.$.quantity": quantity}},
    )
    if result.matched_count == 0:
        sessions.update_one(
            {"customer_id": customer_id},
            {"$push": {"cart": {"product_id": product_id, "quantity": quantity}}},
            upsert=True,
        )


def remove_from_cart(customer_id, product_id):
    sessions.update_one(
        {"customer_id": customer_id},
        {"$pull": {"cart": {"product_id": product_id}}},
    )


def get_cart(customer_id):
    session = sessions.find_one({"customer_id": customer_id})
    return session["cart"] if session else []
