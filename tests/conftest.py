import os
import uuid

import psycopg2
import pytest

# Point the app at a separate database before db.py creates its connection pool.
os.environ["POSTGRES_DB"] = "ecommerce_test"


def recreate_test_database():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5433"),
        dbname="ecommerce",
        user=os.getenv("POSTGRES_USER", "ecommerce"),
        password=os.getenv("POSTGRES_PASSWORD", "ecommerce"),
    )
    conn.autocommit = True  # CREATE/DROP DATABASE cannot run inside a transaction
    with conn.cursor() as cur:
        # FORCE closes any open connections (e.g. from pgAdmin) so the drop can't be blocked.
        cur.execute("DROP DATABASE IF EXISTS ecommerce_test WITH (FORCE)")
        cur.execute("CREATE DATABASE ecommerce_test")
    conn.close()


recreate_test_database()

import cache  # noqa: E402
from create_tables import create_tables  # noqa: E402
from db import get_cursor  # noqa: E402

create_tables()


@pytest.fixture
def customer_id():
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO customers (first_name, last_name, email)
            VALUES ('Test', 'Customer', %s)
            RETURNING customer_id
            """,
            (f"{uuid.uuid4().hex}@example.com",),
        )
        return cur.fetchone()[0]


@pytest.fixture(autouse=True)
def clear_cache():
    # The tests share Redis with the app, so don't leave test data in the cache.
    cache.clear_top_products()
    yield
    cache.clear_top_products()
