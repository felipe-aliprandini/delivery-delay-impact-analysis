-- =============================
-- 1: Loss Aversion

-- =============================

-- Early deliveries 

SELECT
    avg(r.review_score) as med_review,
    avg(julianday(order_delivered_customer_date) - julianday(order_estimated_delivery_date)) as days_late
FROM
    orders AS o
JOIN 
    order_reviews AS r
        ON o.order_id = r.order_id
WHERE
   order_status = 'delivered'
   AND order_delivered_customer_date IS NOT NULL
   AND order_estimated_delivery_date IS NOT NULL
   AND julianday(order_delivered_customer_date) < julianday(order_estimated_delivery_date);


-- Late deliveries:

SELECT
    avg(r.review_score) as med_review,
    avg(julianday(order_delivered_customer_date) - julianday(order_estimated_delivery_date)) as days_late
FROM
    orders AS o
JOIN 
    order_reviews AS r
        ON o.order_id = r.order_id
WHERE
   order_status = 'delivered'
   AND order_delivered_customer_date IS NOT NULL
   AND order_estimated_delivery_date IS NOT NULL
   AND julianday(order_delivered_customer_date) > julianday(order_estimated_delivery_date);


-- Marginal impact of late deliveries:

SELECT 
    ROUND(julianday(order_delivered_customer_date) - 
    julianday(order_estimated_delivery_date)) AS days_diff,
    AVG(r.review_score) AS avg_review,
    COUNT(*) AS total_orders
FROM 
    orders AS o
JOIN order_reviews AS r
    ON o.order_id = r.order_id
WHERE 
    o.order_status = 'delivered'
    AND order_delivered_customer_date IS NOT NULL
    AND order_estimated_delivery_date IS NOT NULL
    AND ROUND(julianday(order_delivered_customer_date) - 
        julianday(order_estimated_delivery_date)) 
        BETWEEN -30 AND 30
GROUP BY
    days_diff
ORDER BY
    days_diff;


