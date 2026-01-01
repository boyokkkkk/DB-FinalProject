-- ==========================================
-- 插入测试数据：单品 (clothing_items)
-- 前提：请确保 sys_user 表里至少有一个用户 (user_id=1)
-- ==========================================

-- 1. 基础白T恤 (上装/夏/休闲)
INSERT INTO clothing_items (user_id, category_id, name, brand, color, season, style, material, price, purchase_date, image_url, notes)
VALUES (
    1, 
    (SELECT category_id FROM categories WHERE category_type = 'top'), 
    '基础纯棉白T恤', 'Uniqlo', 'White', 'Summer', 'Casual', 'Cotton', 99.00, '2024-06-01', 
    'https://via.placeholder.com/300x400/FFFFFF/000000?text=White+T-Shirt', 
    '百搭基础款，透气舒适'
);

-- 2. 经典牛仔裤 (下装/四季/休闲)
INSERT INTO clothing_items (user_id, category_id, name, brand, color, season, style, material, price, purchase_date, image_url, notes)
VALUES (
    1, 
    (SELECT category_id FROM categories WHERE category_type = 'bottom'), 
    '复古直筒牛仔裤', 'Levi''s', 'Blue', 'Autumn', 'Casual', 'Denim', 599.00, '2023-09-15', 
    'https://via.placeholder.com/300x400/3b82f6/FFFFFF?text=Blue+Jeans', 
    '经典版型，适合日常通勤'
);

-- 3. 黑色西装外套 (外套/春秋冬/工作)
INSERT INTO clothing_items (user_id, category_id, name, brand, color, season, style, material, price, purchase_date, image_url, notes)
VALUES (
    1, 
    (SELECT category_id FROM categories WHERE category_type = 'outerwear'), 
    '修身黑色西装', 'Zara', 'Black', 'Spring', 'Work', 'Polyester', 899.00, '2024-03-10', 
    'https://via.placeholder.com/300x400/000000/FFFFFF?text=Black+Blazer', 
    '面试和正式场合专用'
);

-- 4. 碎花连衣裙 (连衣裙/夏/度假)
INSERT INTO clothing_items (user_id, category_id, name, brand, color, season, style, material, price, purchase_date, image_url, notes)
VALUES (
    1, 
    (SELECT category_id FROM categories WHERE category_type = 'dress'), 
    '法式碎花连衣裙', 'Reformation', 'Pink', 'Summer', 'Chic', 'Silk', 1200.00, '2024-05-20', 
    'https://via.placeholder.com/300x400/fbcfe8/000000?text=Floral+Dress', 
    '适合约会和海边度假'
);

-- 5. 运动跑鞋 (鞋子/四季/运动)
INSERT INTO clothing_items (user_id, category_id, name, brand, color, season, style, material, price, purchase_date, image_url, notes)
VALUES (
    1, 
    (SELECT category_id FROM categories WHERE category_type = 'shoes'), 
    '轻量化跑鞋', 'Nike', 'Grey', 'Spring', 'Sporty', 'Mesh', 799.00, '2024-01-01', 
    'https://via.placeholder.com/300x400/94a3b8/FFFFFF?text=Running+Shoes', 
    '晨跑专用，非常轻便'
);

-- 6. 羊毛大衣 (外套/冬/优雅)
INSERT INTO clothing_items (user_id, category_id, name, brand, color, season, style, material, price, purchase_date, image_url, notes)
VALUES (
    1, 
    (SELECT category_id FROM categories WHERE category_type = 'outerwear'), 
    '羊绒大衣', 'MaxMara', 'Camel', 'Winter', 'Formal', 'Wool', 3500.00, '2023-12-10', 
    'https://via.placeholder.com/300x400/d97706/FFFFFF?text=Wool+Coat', 
    '保暖性极好，颜色很高级'
);

-- 7. 帆布手提包 (其他/四季/休闲)
INSERT INTO clothing_items (user_id, category_id, name, brand, color, season, style, material, price, purchase_date, image_url, notes)
VALUES (
    1, 
    (SELECT category_id FROM categories WHERE category_type = 'other'), 
    '大容量托特包', 'L.L.Bean', 'Beige', 'Spring', 'Casual', 'Canvas', 299.00, '2024-04-05', 
    'https://via.placeholder.com/300x400/fef3c7/000000?text=Tote+Bag', 
    '能装电脑，上课通勤都很方便'
);

-- ==========================================
-- (可选) 关联标签数据
-- 如果你想测试标签过滤功能，可以执行以下语句
-- ==========================================

-- 给白T恤 (item_id可能是1) 打上 "夏" 和 "休闲" 标签
INSERT INTO clothing_tags (item_id, tag_id)
SELECT i.item_id, t.tag_id
FROM clothing_items i, tags t
WHERE i.name = '基础纯棉白T恤' AND t.tag_name IN ('夏', '休闲')
ON CONFLICT DO NOTHING;

-- 给西装 (item_id可能是3) 打上 "工作" 和 "正式" 标签
INSERT INTO clothing_tags (item_id, tag_id)
SELECT i.item_id, t.tag_id
FROM clothing_items i, tags t
WHERE i.name = '修身黑色西装' AND t.tag_name IN ('工作', '正式')
ON CONFLICT DO NOTHING;