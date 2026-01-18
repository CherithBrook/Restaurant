-- ===============================
-- 03_base_data.sql
-- 系统初始数据
-- ===============================

-- 1. 桌台
INSERT INTO table_info(table_id, status, seat_count) VALUES
(1,'空闲',4),
(2,'空闲',4),
(3,'空闲',6),
(4,'空闲',2);

-- 2. 菜品分类
INSERT INTO food_type(type_id, type_name) VALUES
(1,'热菜'),
(2,'凉菜'),
(3,'汤羹'),
(4,'主食');

-- 3. 口味选项
INSERT INTO taste_option(taste_id, taste_name) VALUES
(1,'不辣'),
(2,'微辣'),
(3,'中辣'),
(4,'特辣'),
(5,'少油'),
(6,'正常油');

-- 4. 菜品
INSERT INTO food(food_id, food_name, type_id, price, is_sale) VALUES
(1,'水煮肉片',1,38.00,TRUE),
(2,'宫保鸡丁',1,28.00,TRUE),
(3,'凉拌黄瓜',2,12.00,TRUE),
(4,'紫菜蛋花汤',3,10.00,TRUE),
(5,'米饭',4,2.00,TRUE);

-- 5. 菜品-口味关联
-- 水煮肉片：辣度 + 油量（多轮）
INSERT INTO food_taste(food_id, taste_id) VALUES
(1,1),(1,2),(1,3),(1,4),
(1,5),(1,6);

-- 宫保鸡丁：辣度
INSERT INTO food_taste(food_id, taste_id) VALUES
(2,1),(2,2),(2,3);

-- 其他菜品（如米饭）不插入口味记录 → 不需要口味选择

-- 6. 角色
INSERT INTO role(role_id, role_name) VALUES
(1,'顾客'),
(2,'服务员'),
(3,'后厨'),
(4,'经理');

-- 7. 用户
INSERT INTO user_info(user_id, user_name, password, role_id) VALUES
(1,'customer','123456',1),
(2,'waiter','123456',2),
(3,'chef','123456',3),
(4,'manager','123456',4);
