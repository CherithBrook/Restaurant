-- 插入角色数据
INSERT INTO roles (role_name, description)
VALUES 
('顾客', '扫码点餐、加菜、催菜、查看账单'),
('服务员', '开台、代客点餐、退菜、结账'),
('后厨', '查看分单、更新菜品制作状态'),
('经理', '菜品管理、桌台管理、营收统计');

-- 插入测试用户（密码：123456，已加密）
INSERT INTO users (username, password, role_id, real_name)
VALUES 
('customer1', '$2b$12$EixZaYb4xU58Gpq1R0yWbeb00LU5qUaK6xW6X7G9s2bFb0h2e2e2e', 1, '顾客张三'),
('waiter1', '$2b$12$EixZaYb4xU58Gpq1R0yWbeb00LU5qUaK6xW6X7G9s2bFb0h2e2e2e', 2, '服务员李四'),
('chef1', '$2b$12$EixZaYb4xU58Gpq1R0yWbeb00LU5qUaK6xW6X7G9s2bFb0h2e2e2e', 3, '厨师王五'),
('manager1', '$2b$12$EixZaYb4xU58Gpq1R0yWbeb00LU5qUaK6xW6X7G9s2bFb0h2e2e2e', 4, '经理赵六');

-- 插入桌台数据（10张桌台：6张大厅圆桌，4个包间）
INSERT INTO tables (table_number, capacity, table_type)
VALUES 
('T001', 4, '大厅圆桌'),
('T002', 4, '大厅圆桌'),
('T003', 6, '大厅圆桌'),
('T004', 6, '大厅圆桌'),
('T005', 8, '大厅圆桌'),
('T006', 8, '大厅圆桌'),
('V001', 6, '包间'),
('V002', 8, '包间'),
('V003', 10, '包间'),
('V004', 12, '包间');

-- 插入菜品分类
INSERT INTO dish_categories (category_name, description, sort_order)
VALUES 
('热菜', '现炒热菜', 1),
('凉菜', '凉拌菜品', 2),
('汤羹', '汤类菜品', 3),
('主食', '米饭、面条等', 4),
('酒水', '饮料、酒类', 5);

-- 插入口味选项
INSERT INTO taste_options (taste_name, description)
VALUES 
('微辣', '轻度辣味'),
('中辣', '中度辣味'),
('特辣', '重度辣味'),
('少油', '减少用油量'),
('正常油', '标准用油量'),
('免蒜', '不含大蒜'),
('免葱', '不含大葱'),
('加醋', '额外添加醋');

-- 插入菜品数据
INSERT INTO dishes (dish_name, category_id, price, description, sort_order)
VALUES 
('水煮肉片', 1, 48.00, '经典川菜，肉质鲜嫩', 1),
('麻婆豆腐', 1, 28.00, '香辣下饭，豆腐软嫩', 2),
('拍黄瓜', 2, 16.00, '清爽开胃，酸辣可口', 3),
('夫妻肺片', 2, 38.00, '麻辣鲜香，口感丰富', 4),
('番茄蛋汤', 3, 18.00, '酸甜可口，营养丰富', 5),
('冬瓜海带汤', 3, 22.00, '清淡解腻', 6),
('白米饭', 4, 3.00, '香喷喷白米饭', 7),
('担担面', 4, 15.00, '四川特色面条', 8),
('可乐', 5, 6.00, '碳酸饮料', 9),
('雪花啤酒', 5, 8.00, '瓶装啤酒', 10);

-- 插入菜品-口味关联（必选/可选）
INSERT INTO dish_taste_mappings (dish_id, taste_id, is_required)
VALUES 
-- 水煮肉片：必选辣度和用油量
(1, 1, TRUE), (1, 2, TRUE), (1, 3, TRUE), -- 辣度三选一（实际通过应用层控制单选）
(1, 4, TRUE), (1, 5, TRUE), -- 用油量二选一
(1, 6, FALSE), (1, 7, FALSE), -- 可选：免蒜、免葱
-- 麻婆豆腐：必选辣度
(2, 1, TRUE), (2, 2, TRUE), (2, 3, TRUE),
(2, 4, FALSE), (2, 5, FALSE),
-- 拍黄瓜：必选酸甜度（这里用加醋代替）
(3, 8, TRUE),
(3, 6, FALSE), (3, 7, FALSE),
-- 其他菜品默认可选口味
(4, 1, FALSE), (4, 2, FALSE), (4, 3, FALSE),
(5, 6, FALSE), (5, 7, FALSE),
(6, 6, FALSE), (6, 7, FALSE),
(7, 6, FALSE), (7, 7, FALSE),
(8, 1, FALSE), (8, 2, FALSE), (8, 3, FALSE),
(9, 6, FALSE), (10, 6, FALSE);