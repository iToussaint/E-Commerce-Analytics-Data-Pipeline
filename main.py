"""Run the pipeline end to end against the databases started with docker compose.

Expects the tables to exist and sql/sample_data.sql to be loaded (see README).
"""

import time

import cache
from db import add_product, create_order, get_customer_orders, get_top_selling_products, pool
from sessions import add_to_cart, get_cart, remove_from_cart, save_session

CUSTOMER_ID = 1
ROWS_TO_SHOW = 5


def print_title(title):
    print(f"\n=== {title} ===")


def demo_postgres():
    print_title("PostgreSQL: CRUD and transactions")
    product_id = add_product("Demo Jacket", 89.99, 5, {"sizes": ["M", "L"], "colors": ["green"]})
    print(f"add_product() -> product {product_id}")

    order_id = create_order(CUSTOMER_ID, [(product_id, 2), (1, 1)])
    print(f"create_order() -> order {order_id}")

    try:
        create_order(CUSTOMER_ID, [(1, 1), (product_id, 100)])
    except ValueError as error:
        print(f"create_order() with too little stock was rolled back: {error}")

    print(f"get_customer_orders({CUSTOMER_ID}):")
    for order_id, order_date, total in get_customer_orders(CUSTOMER_ID):
        print(f"  order {order_id}  {order_date:%Y-%m-%d}  total {total}")


def timed_top_products():
    start = time.perf_counter()
    products = get_top_selling_products()
    return products, (time.perf_counter() - start) * 1000


def demo_redis():
    print_title("Redis: top 10 best-selling products cache")
    cache.clear_top_products()

    products, elapsed = timed_top_products()
    print(f"First call (PostgreSQL, then cached): {elapsed:.1f} ms")
    _, elapsed = timed_top_products()
    print(f"Second call (Redis): {elapsed:.1f} ms")
    for product in products:
        print(f"  {product['product_id']:>6}  {product['name']:<25} sold {product['total_sold']}")

    create_order(CUSTOMER_ID, [(1, 1)])
    print(f"After a new order the cache is cleared: {cache.get_top_products() is None}")


def demo_mongodb():
    print_title("MongoDB: session and cart")
    save_session(CUSTOMER_ID)
    add_to_cart(CUSTOMER_ID, 10, 2)
    add_to_cart(CUSTOMER_ID, 20, 1)
    add_to_cart(CUSTOMER_ID, 10, 1)
    print(f"Cart after adding items: {get_cart(CUSTOMER_ID)}")
    remove_from_cart(CUSTOMER_ID, 20)
    print(f"Cart after removing product 20: {get_cart(CUSTOMER_ID)}")


def demo_analytics():
    print_title("Analytics: queries from sql/queries.sql")
    with open("sql/queries.sql") as f:
        # Statements end with ";" at the end of a line (comments may contain ";" too).
        statements = [s for s in f.read().split(";\n") if s.strip()]

    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            for number, statement in enumerate(statements, start=1):
                cur.execute(statement)
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
                print(f"\nQuery {number}: {len(rows)} rows, showing up to {ROWS_TO_SHOW}")
                print("  " + " | ".join(columns))
                for row in rows[:ROWS_TO_SHOW]:
                    print("  " + " | ".join(str(value) for value in row))
    finally:
        pool.putconn(conn)


if __name__ == "__main__":
    demo_postgres()
    demo_redis()
    demo_mongodb()
    demo_analytics()
