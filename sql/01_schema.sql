-- 角色表
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户表（关联角色）
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role_id INT NOT NULL,
    real_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 桌台表
CREATE TABLE tables (
    table_id SERIAL PRIMARY KEY,
    table_number VARCHAR(20) NOT NULL UNIQUE,
    capacity INT NOT NULL CHECK (capacity > 0),
    table_type VARCHAR(20) NOT NULL DEFAULT '大厅圆桌', -- 大厅圆桌/包间
    status VARCHAR(20) NOT NULL DEFAULT '空闲',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 菜品分类表
CREATE TABLE dish_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 口味选项表
CREATE TABLE taste_options (
    taste_id SERIAL PRIMARY KEY,
    taste_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 菜品表（关联分类）
CREATE TABLE dishes (
    dish_id SERIAL PRIMARY KEY,
    dish_name VARCHAR(100) NOT NULL UNIQUE,
    category_id INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 菜品-口味关联表（定义必选/可选口味）
CREATE TABLE dish_taste_mappings (
    dish_taste_id SERIAL PRIMARY KEY,
    dish_id INT NOT NULL,
    taste_id INT NOT NULL,
    is_required BOOLEAN NOT NULL DEFAULT FALSE, -- 是否必选口味
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (dish_id, taste_id)
);

-- 订单表（关联桌台和创建用户）
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    table_id INT NOT NULL,
    created_by INT NOT NULL, -- 创建订单的用户ID
    status VARCHAR(20) NOT NULL DEFAULT '未结账',
    discount DECIMAL(5, 2) DEFAULT 1.00, -- 折扣率（0-1）
    total_amount DECIMAL(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单明细表（关联订单和菜品）
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    dish_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    subtotal DECIMAL(12, 2) NOT NULL CHECK (subtotal >= 0),
    taste_choices JSONB NOT NULL, -- 选中的口味（{taste_id: taste_name}）
    is_urgent BOOLEAN DEFAULT FALSE, -- 是否催菜
    status VARCHAR(20) NOT NULL DEFAULT '未制作', -- 未制作/制作中/已完成/已退菜
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 退菜记录表
CREATE TABLE refund_records (
    refund_id SERIAL PRIMARY KEY,
    order_item_id INT NOT NULL,
    refund_reason TEXT NOT NULL,
    refunded_by INT NOT NULL, -- 退菜人ID
    refunded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);