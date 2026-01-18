-- 外键约束
ALTER TABLE food
ADD CONSTRAINT fk_food_type
FOREIGN KEY (type_id) REFERENCES food_type(type_id);

ALTER TABLE food_taste
ADD CONSTRAINT fk_ft_food
FOREIGN KEY (food_id) REFERENCES food(food_id);

ALTER TABLE food_taste
ADD CONSTRAINT fk_ft_taste
FOREIGN KEY (taste_id) REFERENCES taste_option(taste_id);

ALTER TABLE order_main
ADD CONSTRAINT fk_order_table
FOREIGN KEY (table_id) REFERENCES table_info(table_id);

ALTER TABLE order_detail
ADD CONSTRAINT fk_detail_order
FOREIGN KEY (order_id) REFERENCES order_main(order_id);

ALTER TABLE order_detail
ADD CONSTRAINT fk_detail_food
FOREIGN KEY (food_id) REFERENCES food(food_id);

ALTER TABLE order_detail
ADD CONSTRAINT fk_detail_taste
FOREIGN KEY (taste_id) REFERENCES taste_option(taste_id);

ALTER TABLE refund_record
ADD CONSTRAINT fk_refund_detail
FOREIGN KEY (detail_id) REFERENCES order_detail(detail_id);

ALTER TABLE user_info
ADD CONSTRAINT fk_user_role
FOREIGN KEY (role_id) REFERENCES role(role_id);

-- CHECK 约束
ALTER TABLE table_info
ADD CONSTRAINT chk_table_status
CHECK (status IN ('空闲', '占用', '待清理'));

ALTER TABLE order_main
ADD CONSTRAINT chk_order_status
CHECK (status IN ('未结算', '已结算'));

ALTER TABLE order_detail
ADD CONSTRAINT chk_detail_status
CHECK (status IN ('未做', '制作中', '已完成', '已退'));
