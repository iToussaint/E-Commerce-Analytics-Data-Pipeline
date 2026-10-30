import os

from psycopg2.extras import Json
from psycopg2.pool import SimpleConnectionPool

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5433"),
    dbname=os.getenv("POSTGRES_DB", "ecommerce"),
    user=os.getenv("POSTGRES_USER", "ecommerce"),
    password=os.getenv("POSTGRES_PASSWORD", "ecommerce"),
)


def add_product(name, price, stock_quantity, metadata):
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO products (name, price, stock_quantity, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING product_id
                """,
                (name, price, stock_quantity, Json(metadata)),
            )
            return cur.fetchone()[0]
    finally:
        pool.putconn(conn)


def create_order(customer_id, items):
    """Create an order from a list of (product_id, quantity) pairs.

    Runs as a single transaction: if any item fails (unknown product or
    not enough stock), nothing is saved.
    """
    conn = pool.getconn()
    try:
        # "with conn" commits on success and rolls back if an exception is raised.
        with conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO orders (customer_id) VALUES (%s) RETURNING order_id",
                (customer_id,),
            )
            order_id = cur.fetchone()[0]

            for product_id, quantity in items:
                # FOR UPDATE locks the row so concurrent orders can't oversell the stock.
                cur.execute(
                    "SELECT price, stock_quantity FROM products WHERE product_id = %s FOR UPDATE",
                    (product_id,),
                )
                product = cur.fetchone()
                if product is None:
                    raise ValueError(f"Product {product_id} does not exist")
                price, stock_quantity = product
                if stock_quantity < quantity:
                    raise ValueError(f"Not enough stock for product {product_id}")

                cur.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                    (quantity, product_id),
                )
                cur.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, product_id, quantity, price),
                )
            return order_id
    finally:
        pool.putconn(conn)


def get_customer_orders(customer_id):
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT o.order_id, o.order_date, SUM(oi.quantity * oi.unit_price) AS total
                FROM orders o
                JOIN order_items oi ON oi.order_id = o.order_id
                WHERE o.customer_id = %s
                GROUP BY o.order_id, o.order_date
                ORDER BY o.order_date
                """,
                (customer_id,),
            )
            return cur.fetchall()
    finally:
        pool.putconn(conn)
