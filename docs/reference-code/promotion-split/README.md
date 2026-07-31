# 小程序分账系统

仅一级推广 + 0.01 元激活 + 7 天资金冻结自动分账 + 第三方支付托管，完全合规的分账系统。

## 目录结构

```
promotion-split/
├── schema.sql          # 7 张表：users/promoters/promotion_relations/orders/order_splits/agreements/authorizations
├── server.js           # Node.js + Express 后端（10 个 API）
├── cron-jobs.js        # node-cron 定时任务（凌晨2点自动分账 / 凌晨3点退款冲抵）
├── .env.example        # 环境变量模板
├── package.json        # 依赖
├── docker-compose.yml  # Docker 编排（app + mysql8）
└── Dockerfile          # 容器镜像
```

## 数据模型（7 张表）

| 表 | 作用 |
|----|------|
| `users` | 用户（is_promoter 标记） |
| `promoters` | 推广员（收款账户 + 协议签署） |
| `promotion_relations` | 推广关系（仅一级，唯一约束防重复） |
| `orders` | 订单（状态机：1待支付/2已支付/3已完成/4已退款，frozen_until 冻结期） |
| `order_splits` | 分账记录（推广员 90% / 平台 10%，状态：1待分账/2已分账/3已退款） |
| `agreements` | 协议记录（推广员协议/用户协议，含 IP 留痕） |
| `authorizations` | 客户授权记录（授权后才可查看联系方式） |

## API 一览（10 个）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/register` | 用户注册（手机号唯一） |
| POST | `/api/promoter/activate` | 激活推广员（0.01 元订单 + 协议留痕 + 事务） |
| POST | `/api/promoter/deactivate` | 注销推广员（自动退款 0.01 元） |
| POST | `/api/order/create` | 创建订单（推广关系 + 分账记录同事务） |
| POST | `/api/order/pay` | 支付（云购OS托管） |
| POST | `/api/notify` | 支付回调（7 天后 setTimeout 自动分账） |
| POST | `/api/order/refund` | 退款（冲抵分账资金） |
| POST | `/api/authorize` | 客户授权/撤销授权查看手机号 |
| GET | `/api/promoter/:id` | 推广员后台（订单 + 授权列表） |
| GET | `/api/user/:id` | 用户数据（订单 + 推广关系） |

## 合规设计（核心）

1. **仅一级推广**：promotion_relations 唯一约束 `(promoter_id, customer_id)`，无二级间推 → 杜绝传销风险
2. **资金第三方托管**：云购OS（或 MallBook/拉卡拉银行托管）收单 + 分账 → 规避二清风险
3. **7 天资金冻结期**：frozen_until = NOW() + 7 天，售后退款有保障
4. **隐私保护**：authorizations 表记录客户授权，未授权推广员看不到联系方式
5. **全程留痕**：agreements 记录协议签署（IP + 设备信息）

## 定时任务

- `0 2 * * *` 凌晨2点：扫描 `status=3 且 split_status=1 且 frozen_until < NOW()` 的订单执行自动分账
- `0 3 * * *` 凌晨3点：扫描 `status=4 且 split_status=1` 的订单更新为已退款

## 快速启动

```bash
# 本地
npm install
cp .env.example .env   # 填入云购OS密钥
node server.js

# Docker
docker-compose up -d   # 自动建表（schema.sql 挂载到 initdb）
```

## 扩展方向

- 后期可迁移至 MallBook / 拉卡拉银行托管分账系统（替换 yungouApi 封装即可）
- 分账比例可配置化（当前硬编码 0.9/0.1）
- 风控：云端+本地双备份、正规支付服务商、限制宣传话术

## 与 customer-crawler 系统集成

- 现有 `distribution` app（Promoter/Withdrawal/Commission/DistributionOrder/CustomerReport）已实现推广员体系，本系统可作为**真实支付分账层**接入：
  - `Promoter.rate` → 对应 order_splits.promoter_amount 比例
  - `Withdrawal` 提现审核 → 对应云购OS 分账到推广员收款账户
  - `DistributionOrder.status` → 对应 orders.status 状态机
  - 前端 Promotion.vue 的「提现」按钮 → 调用分账 API
