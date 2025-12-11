-- sql/init.sql

-- ==========================================
-- 1. 用户表 (sys_user)
-- ==========================================
DROP TABLE IF EXISTS sys_user;

CREATE TABLE sys_user (
    user_id       SERIAL PRIMARY KEY,        -- 自增主键
    username      VARCHAR(50) NOT NULL UNIQUE, -- 用户名 (唯一)
    password      VARCHAR(100) NOT NULL,     -- 密码 (加密存储)
    avatar        VARCHAR(255),              -- 头像URL (预留)
    create_time   TIMESTAMP DEFAULT NOW()    -- 注册时间
);
