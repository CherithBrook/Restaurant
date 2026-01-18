-- 获取菜品口味选项的存储过程（函数）
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
    WHERE dtm.dish_id = p_dish_id;
END;
$$;

-- 获取菜品必选口味的存储过程（函数）
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
    WHERE dtm.dish_id = p_dish_id AND dtm.is_required = TRUE;
END;
$$;