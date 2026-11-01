from decimal import Decimal

import pytest

from db import add_product, create_order, get_customer_orders, get_cursor


def query_one(sql, params):
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def get_stock(product_id):
    return query_one("SELECT stock_quantity FROM products WHERE product_id = %s", (product_id,))[0]


def test_add_product_stores_metadata_as_jsonb():
    product_id = add_product("Hoodie", 39.99, 5, {"sizes": ["M", "L"], "colors": ["black"]})

    name, metadata = query_one("SELECT name, metadata FROM products WHERE product_id = %s", (product_id,))
    assert name == "Hoodie"
    assert metadata == {"sizes": ["M", "L"], "colors": ["black"]}


def test_create_order_saves_items_and_reduces_stock(customer_id):
    shirt = add_product("T-Shirt", 19.99, 10, {})
    mug = add_product("Mug", 7.50, 3, {})

    order_id = create_order(customer_id, [(shirt, 2), (mug, 1)])

    assert get_stock(shirt) == 8
    assert get_stock(mug) == 2
    quantity, unit_price = query_one(
        "SELECT quantity, unit_price FROM order_items WHERE order_id = %s AND product_id = %s",
        (order_id, shirt),
    )
    assert quantity == 2
    assert unit_price == Decimal("19.99")


def test_create_order_rolls_back_when_stock_is_insufficient(customer_id):
    shirt = add_product("T-Shirt", 19.99, 10, {})
    mug = add_product("Mug", 7.50, 1, {})

    # The shirt is processed first, so its stock is reduced before the mug fails.
    with pytest.raises(ValueError, match="Not enough stock"):
        create_order(customer_id, [(shirt, 2), (mug, 5)])

    assert get_stock(shirt) == 10
    assert get_stock(mug) == 1
    assert query_one("SELECT COUNT(*) FROM orders WHERE customer_id = %s", (customer_id,))[0] == 0


def test_create_order_rejects_unknown_product(customer_id):
    with pytest.raises(ValueError, match="does not exist"):
        create_order(customer_id, [(999_999, 1)])


def test_get_customer_orders_returns_order_totals(customer_id):
    shirt = add_product("T-Shirt", 19.99, 10, {})
    mug = add_product("Mug", 7.50, 10, {})
    order_id = create_order(customer_id, [(shirt, 2), (mug, 1)])

    orders = get_customer_orders(customer_id)

    assert len(orders) == 1
    assert orders[0][0] == order_id
    assert orders[0][2] == Decimal("47.48")
