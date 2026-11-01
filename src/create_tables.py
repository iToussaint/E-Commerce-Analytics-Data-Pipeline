from db import get_cursor


def create_tables():
    with open("sql/schema.sql") as f:
        schema_sql = f.read()

    with get_cursor() as cur:
        cur.execute(schema_sql)


if __name__ == "__main__":
    create_tables()
    print("Tables created.")
