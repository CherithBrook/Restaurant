-- 外键约束
ALTER TABLE users
ADD CONSTRAINT fk_users_roles FOREIGN KEY (role_id) REFERENCES roles (role_id) ON DELETE RESTRICT;

ALTER TABLE dishes
ADD CONSTRAINT fk_dishes_categories FOREIGN KEY (category_id) REFERENCES dish_categories (category_id) ON DELETE RESTRICT;

ALTER TABLE dish_taste_mappings
ADD CONSTRAINT fk_dish_taste_dishes FOREIGN KEY (dish_id) REFERENCES dishes (dish_id) ON DELETE CASCADE,
ADD CONSTRAINT fk_dish_taste_options FOREIGN KEY (taste_id) REFERENCES taste_options (taste_id) ON DELETE CASCADE;

ALTER TABLE orders
ADD CONSTRAINT fk_orders_tables FOREIGN KEY (table_id) REFERENCES tables (table_id) ON DELETE RESTRICT,
ADD CONSTRAINT fk_orders_users FOREIGN KEY (created_by) REFERENCES users (user_id) ON DELETE RESTRICT;

ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_orders FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
ADD CONSTRAINT fk_order_items_dishes FOREIGN KEY (dish_id) REFERENCES dishes (dish_id) ON DELETE RESTRICT;

ALTER TABLE refund_records
ADD CONSTRAINT fk_refund_order_items FOREIGN KEY (order_item_id) REFERENCES order_items (order_item_id) ON DELETE CASCADE,
ADD CONSTRAINT fk_refund_users FOREIGN KEY (refunded_by) REFERENCES users (user_id) ON DELETE RESTRICT;

-- CHECK约束
ALTER TABLE tables
ADD CONSTRAINT chk_tables_status CHECK (status IN ('空闲', '占用', '待清理'));

ALTER TABLE orders
ADD CONSTRAINT chk_orders_status CHECK (status IN ('未结账', '已结账')),
ADD CONSTRAINT chk_orders_discount CHECK (discount BETWEEN 0.00 AND 1.00);

ALTER TABLE order_items
ADD CONSTRAINT chk_order_items_status CHECK (status IN ('未制作', '制作中', '已完成', '已退菜'));

-- 索引优化
CREATE INDEX idx_orders_table_id ON orders (table_id, status);
CREATE INDEX idx_order_items_order_id ON order_items (order_id, status);
CREATE INDEX idx_order_items_is_urgent ON order_items (is_urgent) WHERE is_urgent = TRUE;
CREATE INDEX idx_dishes_category_id ON dishes (category_id, is_active);