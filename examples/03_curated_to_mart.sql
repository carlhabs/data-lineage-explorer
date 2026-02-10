WITH sales_cte AS (
    SELECT order_id, customer_id, region
    FROM curated.orders
)
INSERT INTO mart.sales
SELECT s.order_id,
       s.customer_id,
       d.segment
FROM sales_cte s
JOIN curated.customer_dim d
  ON s.customer_id = d.customer_id;
