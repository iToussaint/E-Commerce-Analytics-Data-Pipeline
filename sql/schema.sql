-- E-commerce schema in 3rd Normal Form.
-- Order totals are not stored: they are derived from order_items.

DROP TABLE IF EXISTS order_items, orders, products, customers;

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name  VARCHAR(50)  NOT NULL,
    last_name   VARCHAR(50)  NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE products (
    product_id     SERIAL PRIMARY KEY,
    name           VARCHAR(100)   NOT NULL,
    price          NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER        NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    metadata       JSONB          NOT NULL DEFAULT '{}'  -- sizes, colors, etc.
);

CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INTEGER   NOT NULL REFERENCES customers (customer_id),
    order_date  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE order_items (
    order_id   INTEGER        NOT NULL REFERENCES orders (order_id) ON DELETE CASCADE,
    product_id INTEGER        NOT NULL REFERENCES products (product_id),
    quantity   INTEGER        NOT NULL CHECK (quantity > 0),
    -- Price at the time of purchase, so later price changes don't alter past orders.
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, product_id)
);
