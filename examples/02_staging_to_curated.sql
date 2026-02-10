INSERT INTO curated.orders
SELECT order_id,
       customer_id,
       region
FROM staging.orders;
