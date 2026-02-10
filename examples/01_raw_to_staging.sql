CREATE TABLE staging.orders AS
SELECT o.order_id,
       o.customer_id,
       c.region
FROM raw.orders o
JOIN raw.customers c
  ON o.customer_id = c.customer_id;
