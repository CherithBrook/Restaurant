-- ===============================
-- 05_procedures.sql
-- 核心业务逻辑（最终版）
-- ===============================

-- 开台（顾客 / 服务员通用）
CREATE OR REPLACE FUNCTION p_open_table(p_table_id INT)
RETURNS INT AS $$
DECLARE oid INT;
BEGIN
  UPDATE table_info SET status='占用'
  WHERE table_id=p_table_id;

  INSERT INTO order_main(table_id,status)
  VALUES(p_table_id,'未结算')
  RETURNING order_id INTO oid;

  RETURN oid;
END;
$$ LANGUAGE plpgsql;

-- 点餐 / 加菜（支持无口味）
CREATE OR REPLACE FUNCTION p_add_order_detail(
  p_order_id INT,
  p_food_id INT,
  p_taste_id INT,
  p_count INT
) RETURNS VOID AS $$
DECLARE p NUMERIC;
BEGIN
  SELECT price INTO p FROM food WHERE food_id=p_food_id;

  INSERT INTO order_detail(
    order_id, food_id, taste_id, count, price, status
  )
  VALUES(
    p_order_id, p_food_id, p_taste_id, p_count, p, '未做'
  );
END;
$$ LANGUAGE plpgsql;

-- 催菜
CREATE OR REPLACE FUNCTION p_urge_detail(p_detail_id INT)
RETURNS VOID AS $$
BEGIN
  UPDATE order_detail
  SET status='制作中'
  WHERE detail_id=p_detail_id
    AND status='未做';
END;
$$ LANGUAGE plpgsql;

-- 退菜
CREATE OR REPLACE FUNCTION p_refund_detail(
  p_detail_id INT,
  p_reason VARCHAR
) RETURNS VOID AS $$
BEGIN
  UPDATE order_detail SET status='已退'
  WHERE detail_id=p_detail_id;

  INSERT INTO refund_record(detail_id,reason)
  VALUES(p_detail_id,p_reason);
END;
$$ LANGUAGE plpgsql;

-- 结账
CREATE OR REPLACE FUNCTION p_checkout(
  p_order_id INT,
  p_discount NUMERIC,
  p_zero NUMERIC
) RETURNS VOID AS $$
DECLARE total NUMERIC;
BEGIN
  SELECT SUM(count*price)
  INTO total
  FROM order_detail
  WHERE order_id=p_order_id
    AND status<>'已退';

  total := total * p_discount - p_zero;

  UPDATE order_main
  SET status='已结算',
      discount=p_discount,
      zero_out=p_zero,
      total_amount=total
  WHERE order_id=p_order_id;

  UPDATE table_info
  SET status='待清理'
  WHERE table_id=(
    SELECT table_id FROM order_main WHERE order_id=p_order_id
  );
END;
$$ LANGUAGE plpgsql;
