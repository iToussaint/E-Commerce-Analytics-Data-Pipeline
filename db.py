import os

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
