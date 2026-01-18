-- 后厨分单视图
CREATE VIEW v_chef_orders AS
SELECT
    d.detail_id,
    f.food_name,
    t.taste_name,
    d.count,
    d.status,
    ft.type_name
FROM order_detail d
JOIN food f ON d.food_id = f.food_id
JOIN taste_option t ON d.taste_id = t.taste_id
JOIN food_type ft ON f.type_id = ft.type_id;

-- 账单视图
CREATE VIEW v_order_bill AS
SELECT
    o.order_id,
    SUM(d.count * d.price) AS total
FROM order_main o
JOIN order_detail d ON o.order_id = d.order_id
GROUP BY o.order_id;

-- 营收视图
CREATE VIEW v_manager_revenue AS
SELECT
    DATE(create_time) AS day,
    SUM(total_amount) AS revenue
FROM order_main
WHERE status = '已结算'
GROUP BY DATE(create_time);
