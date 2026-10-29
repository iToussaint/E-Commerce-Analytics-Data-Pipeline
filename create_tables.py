from db import pool


def create_tables():
    with open("sql/schema.sql") as f:
        schema_sql = f.read()

    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(schema_sql)
    finally:
        pool.putconn(conn)


if __name__ == "__main__":
    create_tables()
    print("Tables created.")
