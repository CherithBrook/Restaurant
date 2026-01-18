-- ===============================
-- 01_schema.sql
-- 数据库逻辑结构：创建所有数据表
-- ===============================

-- 1. 桌台信息表
CREATE TABLE table_info (
    table_id SERIAL PRIMARY KEY,
    status VARCHAR(10) NOT NULL,     -- 空闲 / 占用 / 待清理
    seat_count INT NOT NULL
);

-- 2. 菜品分类表
CREATE TABLE food_type (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(20) NOT NULL
);

-- 3. 口味选项表
CREATE TABLE taste_option (
    taste_id SERIAL PRIMARY KEY,
    taste_name VARCHAR(20) NOT NULL
);

-- 4. 菜品表
CREATE TABLE food (
    food_id SERIAL PRIMARY KEY,
    food_name VARCHAR(50) NOT NULL,
    type_id INT NOT NULL,
    price NUMERIC(8,2) NOT NULL,
    is_sale BOOLEAN NOT NULL DEFAULT TRUE
);

-- 5. 菜品-口味关联表（多对多）
CREATE TABLE food_taste (
    id SERIAL PRIMARY KEY,
    food_id INT NOT NULL,
    taste_id INT NOT NULL
);

-- 6. 订单主表
CREATE TABLE order_main (
    order_id SERIAL PRIMARY KEY,
    table_id INT NOT NULL,
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) NOT NULL,      -- 未结算 / 已结算
    discount NUMERIC(4,2) DEFAULT 1.0,
    zero_out NUMERIC(6,2) DEFAULT 0,
    total_amount NUMERIC(10,2) DEFAULT 0
);

-- 7. 订单明细表
CREATE TABLE order_detail (
    detail_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    food_id INT NOT NULL,
    taste_id INT NOT NULL,
    count INT NOT NULL,
    price NUMERIC(8,2) NOT NULL,
    status VARCHAR(10) NOT NULL       -- 未做 / 制作中 / 已完成 / 已退
);

-- 8. 退菜记录表
CREATE TABLE refund_record (
    refund_id SERIAL PRIMARY KEY,
    detail_id INT NOT NULL,
    reason VARCHAR(100),
    refund_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 9. 角色表
CREATE TABLE role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) NOT NULL
);

-- 10. 用户表
CREATE TABLE user_info (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(30) NOT NULL,
    password VARCHAR(30) NOT NULL,
    role_id INT NOT NULL
);
