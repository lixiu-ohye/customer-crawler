-- ============================================================
-- 小程序分账系统 - 数据库模型设计（MySQL 8.0）
-- 仅一级推广，杜绝传销风险；资金第三方托管，规避二清
-- ============================================================

-- 用户表
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(20) NOT NULL,
  `is_promoter` tinyint(1) DEFAULT 0,
  `promoter_activated_at` datetime DEFAULT NULL,
  `promoter_refunded` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 推广员表
CREATE TABLE `promoters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `payment_account` varchar(100) NOT NULL COMMENT '支付宝/银行卡号',
  `payment_name` varchar(50) DEFAULT NULL COMMENT '收款人姓名',
  `agreement_signed` tinyint(1) DEFAULT 0,
  `agreement_signed_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推广员表';

-- 推广关系表（仅一级）
CREATE TABLE `promotion_relations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `promoter_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `promoter_customer` (`promoter_id`,`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推广关系表（仅一级）';

-- 订单表
CREATE TABLE `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_no` varchar(50) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `promoter_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` tinyint(1) DEFAULT 1 COMMENT '1-待支付 2-已支付 3-已完成 4-已退款',
  `frozen_until` datetime DEFAULT NULL,
  `payment_no` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_no` (`order_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 订单分账表
CREATE TABLE `order_splits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `promoter_amount` decimal(10,2) NOT NULL,
  `platform_fee` decimal(10,2) NOT NULL,
  `split_status` tinyint(1) DEFAULT 1 COMMENT '1-待分账 2-已分账 3-已退款',
  `split_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单分账表';

-- 协议记录表
CREATE TABLE `agreements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `agreement_type` varchar(20) NOT NULL COMMENT 'promoter-推广员协议 user-用户协议',
  `content` text NOT NULL,
  `signed_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `ip_address` varchar(45) DEFAULT NULL,
  `device_info` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='协议记录表';

-- 授权记录表
CREATE TABLE `authorizations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `promoter_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `authorized` tinyint(1) DEFAULT 0,
  `authorized_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='授权记录表（客户授权推广员查看联系方式）';
