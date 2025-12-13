-- ==========================================
-- 0. 清理旧表 (注意顺序，先删依赖表)
-- ==========================================
DROP TABLE IF EXISTS outfit_ref CASCADE;
DROP TABLE IF EXISTS outfit CASCADE;
DROP TABLE IF EXISTS clothing_tags CASCADE;
DROP TABLE IF EXISTS clothing_items CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS sys_user CASCADE;

-- ==========================================
-- 1. 用户表 (sys_user)
-- ==========================================
CREATE TABLE sys_user (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(50) NOT NULL UNIQUE,
    password      VARCHAR(100) NOT NULL,
    avatar        VARCHAR(255),
    create_time   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 2. 分类与标签 (基础字典表)
-- ==========================================
CREATE TABLE categories (
    category_id   SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    category_type VARCHAR(20) NOT NULL CHECK (
        category_type IN ('top', 'bottom', 'outerwear', 'dress', 'shoes', 'other')
    ),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_type)
);

CREATE TABLE tags (
    tag_id        SERIAL PRIMARY KEY,
    tag_name      VARCHAR(50) NOT NULL,
    tag_type      VARCHAR(20) NOT NULL CHECK (
        tag_type IN ('season', 'occasion', 'style', 'color')
    ),
    UNIQUE(tag_name, tag_type)
);

-- ==========================================
-- 3. 衣物单品表 (clothing_items)
-- ==========================================
CREATE TABLE clothing_items (
    item_id       SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES sys_user(user_id) ON DELETE CASCADE,
    category_id   INT REFERENCES categories(category_id) ON DELETE CASCADE,
    name          VARCHAR(100) NOT NULL,
    brand         VARCHAR(100),
    color         VARCHAR(50),
    season        VARCHAR(20),
    occasion      VARCHAR(50),
    style         VARCHAR(50),
    material      VARCHAR(100),
    purchase_date DATE,
    price         DECIMAL(10,2),
    image_url     VARCHAR(500),
    notes         TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 关联表：衣物-标签 (多对多)
CREATE TABLE clothing_tags (
    id            SERIAL PRIMARY KEY,
    item_id       INT REFERENCES clothing_items(item_id) ON DELETE CASCADE,
    tag_id        INT REFERENCES tags(tag_id) ON DELETE CASCADE,
    UNIQUE(item_id, tag_id)
);

-- ==========================================
-- 4. 搭配系统 (Outfit & OutfitRef)
-- ==========================================
CREATE TABLE outfit (
    outfit_id     SERIAL PRIMARY KEY,
    user_id       INT NOT NULL REFERENCES sys_user(user_id) ON DELETE CASCADE,
    name          VARCHAR(100) NOT NULL,
    description   TEXT,
    season        VARCHAR(50),
    style         VARCHAR(50),
    image_url     VARCHAR(255),
    create_time   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE outfit_ref (
    outfit_id     INT NOT NULL REFERENCES outfit(outfit_id) ON DELETE CASCADE,
    item_id       INT NOT NULL REFERENCES clothing_items(item_id) ON DELETE CASCADE,
    
    -- 画布位置信息
    position_x    REAL DEFAULT 0.0,
    position_y    REAL DEFAULT 0.0,
    rotation      REAL DEFAULT 0.0,
    scale_x       REAL DEFAULT 1.0,
    scale_y       REAL DEFAULT 1.0,
    z_index       INT DEFAULT 0,
    
    PRIMARY KEY (outfit_id, item_id)
);

-- ==========================================
-- 5. 索引优化
-- ==========================================
CREATE INDEX idx_clothing_items_category ON clothing_items(category_id);
CREATE INDEX idx_clothing_items_user ON clothing_items(user_id);
CREATE INDEX idx_clothing_items_name ON clothing_items(name);
CREATE INDEX idx_clothing_tags_item ON clothing_tags(item_id);
CREATE INDEX idx_outfit_user ON outfit(user_id);

-- ==========================================
-- 6. 初始化数据
-- ==========================================

-- 初始化分类
INSERT INTO categories (category_name, category_type)
SELECT '上装', 'top' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE category_type = 'top');
INSERT INTO categories (category_name, category_type)
SELECT '下装', 'bottom' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE category_type = 'bottom');
INSERT INTO categories (category_name, category_type)
SELECT '外套', 'outerwear' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE category_type = 'outerwear');
INSERT INTO categories (category_name, category_type)
SELECT '连衣裙', 'dress' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE category_type = 'dress');
INSERT INTO categories (category_name, category_type)
SELECT '鞋子', 'shoes' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE category_type = 'shoes');
INSERT INTO categories (category_name, category_type)
SELECT '其他', 'other' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE category_type = 'other');

-- 初始化标签 (已修正：替换掉报错的 ON CONFLICT 语法)
INSERT INTO tags (tag_name, tag_type) SELECT '春', 'season' WHERE NOT EXISTS (SELECT 1 FROM tags WHERE tag_name = '春' AND tag_type = 'season');
INSERT INTO tags (tag_name, tag_type) SELECT '夏', 'season' WHERE NOT EXISTS (SELECT 1 FROM tags WHERE tag_name = '夏' AND tag_type = 'season');
INSERT INTO tags (tag_name, tag_type) SELECT '秋', 'season' WHERE NOT EXISTS (SELECT 1 FROM tags WHERE tag_name = '秋' AND tag_type = 'season');
INSERT INTO tags (tag_name, tag_type) SELECT '冬', 'season' WHERE NOT EXISTS (SELECT 1 FROM tags WHERE tag_name = '冬' AND tag_type = 'season');

INSERT INTO tags (tag_name, tag_type) SELECT '休闲', 'occasion' WHERE NOT EXISTS (SELECT 1 FROM tags WHERE tag_name = '休闲' AND tag_type = 'occasion');
INSERT INTO tags (tag_name, tag_type) SELECT '工作', 'occasion' WHERE NOT EXISTS (SELECT 1 FROM tags WHERE tag_name = '工作' AND tag_type = 'occasion');
INSERT INTO tags (tag_name, tag_type) SELECT '正式', 'occasion' WHERE NOT EXISTS (SELECT 1 FROM tags WHERE tag_name = '正式' AND tag_type = 'occasion');
INSERT INTO tags (tag_name, tag_type) SELECT '运动', 'occasion' WHERE NOT EXISTS (SELECT 1 FROM tags WHERE tag_name = '运动' AND tag_type = 'occasion');

SELECT '数据库初始化完成！表结构已统一。' AS message;