-- ============================================
-- 视图定义（后厨分单 / 账单 / 营收统计）
-- 修正版：修复 GROUP BY + ORDER BY 冲突
-- ============================================


-- 1. 后厨分单视图（按冷热菜分类，显示未完成菜品）
CREATE OR REPLACE VIEW chef_order_view AS
SELECT 
    oi.order_item_id,
    o.order_id,
    t.table_number,
    dc.category_name,
    dc.sort_order,
    d.dish_name,
    oi.quantity,
    oi.taste_choices,
    oi.is_urgent,
    oi.status,
    oi.created_at
FROM 
    order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN tables t ON o.table_id = t.table_id
JOIN dishes d ON oi.dish_id = d.dish_id
JOIN dish_categories dc ON d.category_id = dc.category_id
WHERE 
    oi.status IN ('未制作', '制作中')
ORDER BY 
    dc.sort_order,
    oi.is_urgent DESC,
    oi.created_at;


-- 2. 账单视图（按订单汇总消费明细）
CREATE OR REPLACE VIEW bill_view AS
SELECT 
    o.order_id,
    t.table_number,
    u.real_name AS created_by,
    o.status AS order_status,
    d.dish_name,
    oi.quantity,
    oi.unit_price,
    oi.subtotal,
    oi.taste_choices,
    oi.status AS item_status,
    COALESCE(rr.refund_reason, '') AS refund_reason,
    o.discount,
    o.total_amount
FROM 
    orders o
JOIN tables t ON o.table_id = t.table_id
JOIN users u ON o.created_by = u.user_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN dishes d ON oi.dish_id = d.dish_id
LEFT JOIN refund_records rr ON oi.order_item_id = rr.order_item_id
ORDER BY 
    o.created_at DESC,
    oi.order_item_id;


-- 3. 营收统计视图（按日期、分类统计）
CREATE OR REPLACE VIEW revenue_view AS
SELECT 
    DATE(o.created_at) AS business_date,
    dc.category_name,
    dc.sort_order,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(oi.order_item_id) AS item_count,
    SUM(oi.subtotal) AS gross_amount,
    SUM(
        CASE 
            WHEN oi.status != '已退菜' THEN oi.subtotal 
            ELSE 0 
        END
    ) AS net_amount,
    COUNT(DISTINCT o.table_id) AS table_count
FROM 
    orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN dishes d ON oi.dish_id = d.dish_id
JOIN dish_categories dc ON d.category_id = dc.category_id
WHERE 
    o.status = '已结账'
GROUP BY 
    DATE(o.created_at),
    dc.category_name,
    dc.sort_order
ORDER BY 
    business_date DESC,
    dc.sort_order;
