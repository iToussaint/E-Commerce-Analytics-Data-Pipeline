import cache
from db import add_product, create_order, get_top_selling_products


def test_top_products_are_cached_in_redis(customer_id):
    product_id = add_product("Cap", 12.00, 10, {})
    create_order(customer_id, [(product_id, 3)])

    products = get_top_selling_products()

    assert cache.get_top_products() == products
    assert len(products) <= 10
    totals = [product["total_sold"] for product in products]
    assert totals == sorted(totals, reverse=True)


def test_second_call_is_served_from_cache():
    cache.save_top_products([{"product_id": 1, "name": "Cached", "total_sold": 1}])

    assert get_top_selling_products() == [{"product_id": 1, "name": "Cached", "total_sold": 1}]


def test_create_order_clears_the_cache(customer_id):
    product_id = add_product("Cap", 12.00, 10, {})
    get_top_selling_products()
    assert cache.get_top_products() is not None

    create_order(customer_id, [(product_id, 1)])

    assert cache.get_top_products() is None
