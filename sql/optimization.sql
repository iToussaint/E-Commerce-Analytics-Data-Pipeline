-- Query optimization: run each step in order and compare the EXPLAIN ANALYZE output.
-- Run against a freshly loaded database (no indexes yet).

-- Step 1: orders of one customer (the query behind get_customer_orders()), BEFORE indexing.
EXPLAIN ANALYZE
SELECT o.order_id, o.order_date, SUM(oi.quantity * oi.unit_price) AS total
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.customer_id = 42
GROUP BY o.order_id, o.order_date;

-- Step 2: B-tree index on orders.customer_id.
-- PostgreSQL does not index foreign key columns automatically.
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
ANALYZE orders;

-- Step 3: the same query AFTER indexing.
EXPLAIN ANALYZE
SELECT o.order_id, o.order_date, SUM(oi.quantity * oi.unit_price) AS total
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.customer_id = 42
GROUP BY o.order_id, o.order_date;

-- Step 4: products available in red (JSONB containment), BEFORE indexing.
EXPLAIN ANALYZE
SELECT product_id, name
FROM products
WHERE metadata @> '{"colors": ["red"]}';

-- Step 5: GIN index on products.metadata, which supports the @> operator.
CREATE INDEX idx_products_metadata ON products USING GIN (metadata);
ANALYZE products;

-- Step 6: the same query AFTER indexing.
EXPLAIN ANALYZE
SELECT product_id, name
FROM products
WHERE metadata @> '{"colors": ["red"]}';
