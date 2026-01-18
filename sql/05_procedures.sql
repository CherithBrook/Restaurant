-- =================================================
-- 存储过程定义（修正版）
-- 修复：DEFAULT + OUT 参数冲突问题
-- =================================================


-- 1. 开台存储过程
CREATE OR REPLACE PROCEDURE open_table(
    p_table_id INT,
    p_created_by INT,
    OUT p_order_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_table_status VARCHAR(20);
BEGIN
    SELECT status INTO v_table_status FROM tables WHERE table_id = p_table_id;

    IF v_table_status != '空闲' THEN
        RAISE EXCEPTION '桌台当前状态为：%，无法开台', v_table_status;
    END IF;

    INSERT INTO orders (table_id, created_by, status, discount, total_amount)
    VALUES (p_table_id, p_created_by, '未结账', 1.00, 0.00)
    RETURNING order_id INTO p_order_id;

    UPDATE tables 
    SET status = '占用', updated_at = CURRENT_TIMESTAMP 
    WHERE table_id = p_table_id;
END;
$$;


-- 2. 点餐 / 加菜存储过程
CREATE OR REPLACE PROCEDURE place_order(
    p_table_id INT,
    p_created_by INT,
    p_dish_list JSONB,
    OUT p_order_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_id INT;
    v_dish_id INT;
    v_quantity INT;
    v_taste_choices JSONB;
    v_unit_price DECIMAL(10,2);
    v_subtotal DECIMAL(12,2);
    v_required_tastes INT;
    v_selected_tastes INT;
BEGIN
    SELECT order_id INTO v_order_id
    FROM orders 
    WHERE table_id = p_table_id AND status = '未结账'
    ORDER BY created_at DESC LIMIT 1;

    IF v_order_id IS NULL THEN
        CALL open_table(p_table_id, p_created_by, v_order_id);
    END IF;

    p_order_id := v_order_id;

    FOR i IN 0..jsonb_array_length(p_dish_list) - 1 LOOP
        v_dish_id := (p_dish_list -> i ->> 'dish_id')::INT;
        v_quantity := (p_dish_list -> i ->> 'quantity')::INT;
        v_taste_choices := p_dish_list -> i -> 'taste_choices';

        IF NOT EXISTS (
            SELECT 1 FROM dishes WHERE dish_id = v_dish_id AND is_active = TRUE
        ) THEN
            RAISE EXCEPTION '菜品ID：% 不存在或已下架', v_dish_id;
        END IF;

        SELECT COUNT(*) INTO v_required_tastes
        FROM dish_taste_mappings
        WHERE dish_id = v_dish_id AND is_required = TRUE;

        SELECT COUNT(*) INTO v_selected_tastes
        FROM jsonb_object_keys(v_taste_choices) AS tc
        JOIN dish_taste_mappings dtm ON tc::INT = dtm.taste_id
        WHERE dtm.dish_id = v_dish_id AND dtm.is_required = TRUE;

        IF v_selected_tastes < v_required_tastes THEN
            RAISE EXCEPTION '菜品：% 未选择全部必选口味',
                (SELECT dish_name FROM dishes WHERE dish_id = v_dish_id);
        END IF;

        SELECT price INTO v_unit_price FROM dishes WHERE dish_id = v_dish_id;
        v_subtotal := v_unit_price * v_quantity;

        INSERT INTO order_items (
            order_id, dish_id, quantity, unit_price, subtotal, taste_choices
        )
        VALUES (
            v_order_id, v_dish_id, v_quantity, v_unit_price, v_subtotal, v_taste_choices
        );
    END LOOP;

    UPDATE orders
    SET total_amount = (
        SELECT COALESCE(
            SUM(CASE WHEN status != '已退菜' THEN subtotal ELSE 0 END), 0
        )
        FROM order_items WHERE order_id = v_order_id
    ) * discount,
    updated_at = CURRENT_TIMESTAMP
    WHERE order_id = v_order_id;
END;
$$;


-- 3. 催菜
CREATE OR REPLACE PROCEDURE urge_dish(
    p_order_item_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_item_status VARCHAR(20);
BEGIN
    SELECT status INTO v_item_status
    FROM order_items WHERE order_item_id = p_order_item_id;

    IF v_item_status IN ('已完成', '已退菜') THEN
        RAISE EXCEPTION '菜品状态为：%，无法催菜', v_item_status;
    END IF;

    UPDATE order_items
    SET is_urgent = TRUE, updated_at = CURRENT_TIMESTAMP
    WHERE order_item_id = p_order_item_id;
END;
$$;


-- 4. 退菜
CREATE OR REPLACE PROCEDURE refund_dish(
    p_order_item_id INT,
    p_refund_reason TEXT,
    p_refunded_by INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_item_status VARCHAR(20);
    v_order_id INT;
BEGIN
    SELECT status, order_id
    INTO v_item_status, v_order_id
    FROM order_items WHERE order_item_id = p_order_item_id;

    IF v_item_status IN ('已完成', '已退菜') THEN
        RAISE EXCEPTION '菜品状态为：%，无法退菜', v_item_status;
    END IF;

    UPDATE order_items
    SET status = '已退菜', updated_at = CURRENT_TIMESTAMP
    WHERE order_item_id = p_order_item_id;

    INSERT INTO refund_records (order_item_id, refund_reason, refunded_by)
    VALUES (p_order_item_id, p_refund_reason, p_refunded_by);

    UPDATE orders
    SET total_amount = (
        SELECT COALESCE(
            SUM(CASE WHEN status != '已退菜' THEN subtotal ELSE 0 END), 0
        )
        FROM order_items WHERE order_id = v_order_id
    ) * discount,
    updated_at = CURRENT_TIMESTAMP
    WHERE order_id = v_order_id;
END;
$$;


-- 5. 结账（⚠️ 修复：不再使用 OUT 参数）
CREATE OR REPLACE PROCEDURE settle_bill(
    p_table_id INT,
    p_discount DECIMAL(5,2)
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
    WHERE order_id = v_order_id;

    UPDATE tables
    SET status = '待清理', updated_at = CURRENT_TIMESTAMP
    WHERE table_id = p_table_id;
END;
$$;


-- 6. 后厨更新菜品状态
CREATE OR REPLACE PROCEDURE update_dish_status(
    p_order_item_id INT,
    p_new_status VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_new_status NOT IN ('未制作', '制作中', '已完成') THEN
        RAISE EXCEPTION '无效状态：%', p_new_status;
    END IF;

    UPDATE order_items
    SET status = p_new_status, updated_at = CURRENT_TIMESTAMP
    WHERE order_item_id = p_order_item_id;
END;
$$;
