-- ============================================================
-- 补充：distribution（分销体系）+ keywords（推广员关注行业）表
-- 追加到 scripts/init.sql 末尾（若重复执行请先 DROP）
-- ============================================================

-- 推广员
CREATE TABLE IF NOT EXISTS promoter (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    invite_code VARCHAR(16) NOT NULL UNIQUE COMMENT '邀请码 INV+5位',
    rate DECIMAL(5,4) NOT NULL DEFAULT 0.2000 COMMENT '返佣比例 0.20',
    status VARCHAR(16) NOT NULL DEFAULT 'active' COMMENT 'active/frozen',
    total_earned DECIMAL(12,4) NOT NULL DEFAULT 0 COMMENT '累计佣金',
    withdrawn_total DECIMAL(12,4) NOT NULL DEFAULT 0 COMMENT '已提现累计',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_promoter_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推广员';

-- 提现记录
CREATE TABLE IF NOT EXISTS withdrawal (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    withdrawal_id VARCHAR(32) NOT NULL UNIQUE COMMENT 'wd_+时间戳',
    promoter_id BIGINT NOT NULL,
    amount DECIMAL(12,4) NOT NULL COMMENT '提现金额',
    channel VARCHAR(16) NOT NULL DEFAULT 'wechat' COMMENT 'wechat/alipay',
    status VARCHAR(16) NOT NULL DEFAULT 'pending' COMMENT 'pending/approved/rejected',
    payout_id VARCHAR(32) NULL COMMENT '第三方打款流水号',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL,
    KEY idx_withdrawal_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提现';

-- 推广海报
CREATE TABLE IF NOT EXISTS promo_poster (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    promoter_id BIGINT NOT NULL,
    title VARCHAR(64) NOT NULL,
    qr_url VARCHAR(255) NULL,
    invite_code VARCHAR(16) NOT NULL,
    click_count INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推广海报';

-- 分销订单（0.01 元体验包等）
CREATE TABLE IF NOT EXISTS distribution_order (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(32) NOT NULL UNIQUE COMMENT 'ord_+时间戳',
    user_id BIGINT NOT NULL,
    promoter_id BIGINT NULL COMMENT '推广员（可空=自然注册）',
    amount DECIMAL(10,2) NOT NULL COMMENT '订单金额',
    status VARCHAR(16) NOT NULL DEFAULT 'pending' COMMENT 'pending/paid/refunded',
    commission_amount DECIMAL(12,4) NOT NULL DEFAULT 0 COMMENT '佣金（4位小数）',
    commission_status VARCHAR(16) NOT NULL DEFAULT 'pending' COMMENT 'pending/settled',
    product_name VARCHAR(64) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at DATETIME NULL,
    KEY idx_dist_order_user (user_id),
    KEY idx_dist_order_promoter (promoter_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分销订单';

-- 客户登记报表
CREATE TABLE IF NOT EXISTS customer_report (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    promoter_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    order_id VARCHAR(32) NULL,
    customer_name VARCHAR(64) NULL,
    phone VARCHAR(32) NULL,
    note VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_cust_report_promoter (promoter_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户登记报表';

-- 佣金记录
CREATE TABLE IF NOT EXISTS commission (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    promoter_id BIGINT NOT NULL,
    order_id VARCHAR(32) NOT NULL,
    amount DECIMAL(12,4) NOT NULL COMMENT '佣金金额（4位小数）',
    status VARCHAR(16) NOT NULL DEFAULT 'pending' COMMENT 'pending/settled',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_commission_promoter (promoter_id),
    UNIQUE KEY uk_commission_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='佣金';

-- 推广员关注行业
CREATE TABLE IF NOT EXISTS promoter_industry (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '关联 sys_user.id',
    industry_id INT NOT NULL COMMENT '行业ID（1-13）',
    industry_name VARCHAR(64) NOT NULL COMMENT '行业名冗余',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_promoter_industry (user_id, industry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推广员关注行业';
