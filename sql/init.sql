-- sql/init.sql

-- ==========================================
-- 1. 用户表 (sys_user)
-- ==========================================
DROP TABLE IF EXISTS sys_user CASCADE;

CREATE TABLE sys_user (
    user_id       SERIAL PRIMARY KEY,        -- 自增主键
    username      VARCHAR(50) NOT NULL UNIQUE, -- 用户名 (唯一)
    password      VARCHAR(100) NOT NULL,     -- 密码 (加密存储)
    avatar        VARCHAR(255),              -- 头像URL (预留)
    create_time   TIMESTAMP DEFAULT NOW()    -- 注册时间
);

-- ==========================================
-- 2. Item
-- ==========================================
DROP TABLE IF EXISTS item CASCADE;

CREATE TABLE item (
    item_id       SERIAL PRIMARY KEY,
    user_id       INT NOT NULL REFERENCES sys_user(user_id) ON DELETE CASCADE, -- user
    name          VARCHAR(100) NOT NULL,
    category      VARCHAR(50) NOT NULL,
    image_url     VARCHAR(255),
    color         VARCHAR(50),
    season        VARCHAR(50),
    style         VARCHAR(50),
    purchase_date TIMESTAMP,
    create_time   TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 3.Outfit
-- ==========================================
DROP TABLE IF EXISTS outfit CASCADE;

CREATE TABLE outfit (
    outfit_id     SERIAL PRIMARY KEY,
    user_id       INT NOT NULL REFERENCES sys_user(user_id) ON DELETE CASCADE,
    name          VARCHAR(100) NOT NULL,
    description   TEXT,
    season        VARCHAR(50),
    style         VARCHAR(50),
    image_url     VARCHAR(255),
    create_time   TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 4.Outfit_ref
-- ==========================================
DROP TABLE IF EXISTS outfit_ref CASCADE;

CREATE TABLE outfit_ref (
    outfit_id     INT NOT NULL REFERENCES outfit(outfit_id) ON DELETE CASCADE,
    item_id       INT NOT NULL REFERENCES item(item_id) ON DELETE CASCADE,
    position_x    REAL DEFAULT 0.0,
    position_y    REAL DEFAULT 0.0,
    rotation      REAL DEFAULT 0.0,
    scale_x       REAL DEFAULT 1.0,
    scale_y       REAL DEFAULT 1.0,
    z_index       INT DEFAULT 0,
    
    PRIMARY KEY (outfit_id, item_id)
);