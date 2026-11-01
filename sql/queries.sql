-- Analytical queries for reporting.

-- 1. Rank products by total revenue (window function).
--    RANK() gives products with equal revenue the same rank.
SELECT
    p.product_id,
    p.name,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS revenue_rank
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
GROUP BY p.product_id, p.name
ORDER BY revenue_rank
LIMIT 10;

-- 2. Revenue per customer (CTE), top 10 customers.
WITH customer_revenue AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY o.customer_id
)
SELECT c.customer_id, c.first_name, c.last_name, cr.order_count, cr.revenue
FROM customer_revenue cr
JOIN customers c ON c.customer_id = cr.customer_id
ORDER BY cr.revenue DESC
LIMIT 10;

-- 3. JSONB metadata queries.

-- Products available in red (@> means "contains"; this can use the GIN index).
SELECT product_id, name, metadata
FROM products
WHERE metadata @> '{"colors": ["red"]}';

-- Products available in size XL.
SELECT product_id, name, metadata -> 'sizes' AS sizes
FROM products
WHERE metadata @> '{"sizes": ["XL"]}';
