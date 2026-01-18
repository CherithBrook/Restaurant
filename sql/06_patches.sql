-- =================================================
-- 缺失的存储过程补丁文件
-- =================================================

-- 1. 获取菜品口味选项的函数
CREATE OR REPLACE FUNCTION get_dish_tastes(p_dish_id INT)
RETURNS TABLE (
    taste_id INT,
    taste_name VARCHAR,
    is_required BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.taste_id,
        t.taste_name,
        dtm.is_required
    FROM taste_options t
    JOIN dish_taste_mappings dtm ON t.taste_id = dtm.taste_id
    WHERE dtm.dish_id = p_dish_id
    ORDER BY dtm.is_required DESC, t.taste_name;
END;
$$;

-- 2. 获取菜品必选口味的函数
CREATE OR REPLACE FUNCTION get_required_tastes(p_dish_id INT)
RETURNS TABLE (
    taste_id INT,
    taste_name VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.taste_id,
        t.taste_name
    FROM taste_options t
    JOIN dish_taste_mappings dtm ON t.taste_id = dtm.taste_id
    WHERE dtm.dish_id = p_dish_id AND dtm.is_required = TRUE
    ORDER BY t.taste_name;
END;
$$;

-- 3. 改进的结账存储过程（返回总金额）
CREATE OR REPLACE PROCEDURE settle_bill_with_return(
    p_table_id INT,
    p_discount DECIMAL(5,2),
    OUT p_total_amount DECIMAL(12,2)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_id INT;
BEGIN
    SELECT order_id INTO v_order_id
    FROM orders
    WHERE table_id = p_table_id AND status = '未结账'
    ORDER BY created_at DESC LIMIT 1;

    IF v_order_id IS NULL THEN
        RAISE EXCEPTION '桌台：% 无未结账订单',
            (SELECT table_number FROM tables WHERE table_id = p_table_id);
    END IF;

    IF p_discount < 0.00 OR p_discount > 1.00 THEN
        RAISE EXCEPTION '折扣率必须在0-1之间';
    END IF;

    UPDATE orders
    SET discount = p_discount,
        total_amount = (
            SELECT COALESCE(
                SUM(CASE WHEN status != '已退菜' THEN subtotal ELSE 0 END), 0
            )
            FROM order_items WHERE order_id = v_order_id
        ) * p_discount,
        status = '已结账',
        updated_at = CURRENT_TIMESTAMP
    WHERE order_id = v_order_id
    RETURNING total_amount INTO p_total_amount;

    UPDATE tables
    SET status = '待清理', updated_at = CURRENT_TIMESTAMP
    WHERE table_id = p_table_id;
END;
$$;

-- 4. 获取桌台当前订单的函数
CREATE OR REPLACE FUNCTION get_table_current_order(p_table_id INT)
RETURNS TABLE (
    order_id INT,
    table_number VARCHAR,
    created_by VARCHAR,
    total_amount DECIMAL(12,2),
    discount DECIMAL(5,2),
    status VARCHAR,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.order_id,
        t.table_number,
        u.real_name as created_by,
        o.total_amount,
        o.discount,
        o.status,
        o.created_at
    FROM orders o
    JOIN tables t ON o.table_id = t.table_id
    JOIN users u ON o.created_by = u.user_id
    WHERE o.table_id = p_table_id AND o.status = '未结账'
    ORDER BY o.created_at DESC
    LIMIT 1;
END;
$$;

-- 5. 获取菜品详细信息的函数
CREATE OR REPLACE FUNCTION get_dish_details(p_dish_id INT)
RETURNS TABLE (
    dish_id INT,
    dish_name VARCHAR,
    category_name VARCHAR,
    price DECIMAL(10,2),
    description TEXT,
    is_active BOOLEAN,
    taste_options JSON
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.dish_id,
        d.dish_name,
        dc.category_name,
        d.price,
        d.description,
        d.is_active,
        COALESCE(
            json_agg(
                json_build_object(
                    'taste_id', t.taste_id,
                    'taste_name', t.taste_name,
                    'is_required', dtm.is_required
                )
            ) FILTER (WHERE t.taste_id IS NOT NULL),
            '[]'::json
        ) as taste_options
    FROM dishes d
    JOIN dish_categories dc ON d.category_id = dc.category_id
    LEFT JOIN dish_taste_mappings dtm ON d.dish_id = dtm.dish_id
    LEFT JOIN taste_options t ON dtm.taste_id = t.taste_id
    WHERE d.dish_id = p_dish_id
    GROUP BY d.dish_id, d.dish_name, dc.category_name, d.price, d.description, d.is_active;
END;
$$;

-- 6. 清理待清理桌台的存储过程
CREATE OR REPLACE PROCEDURE clean_table(p_table_id INT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_table_status VARCHAR(20);
BEGIN
    SELECT status INTO v_table_status FROM tables WHERE table_id = p_table_id;
    
    IF v_table_status != '待清理' THEN
        RAISE EXCEPTION '桌台当前状态为：%，无法清理', v_table_status;
    END IF;
    
    UPDATE tables 
    SET status = '空闲', updated_at = CURRENT_TIMESTAMP 
    WHERE table_id = p_table_id;
    
    RAISE NOTICE '桌台清理完成，状态已更新为空闲';
END;
$$;