# 生产 MySQL 部署指南（customer-crawler）

> 本地开发默认 SQLite（开箱即用）；生产环境通过 `DATABASE_URL` 环境变量一键切换 MySQL/PostgreSQL，**代码零改动**。

## 一、前置条件

- Python 3.11+（本机：QClaw 内置 Python，`python` 命令即 Django 4.2.30 环境）
- MySQL 5.7+ / 8.0（本机未装，需自备或使用云数据库）
- 依赖：`pymysql`、`dj-database-url`（已安装到后端环境，见下）

## 二、安装依赖（已执行 ✅）

```bash
python -m pip install pymysql dj-database-url -i https://pypi.tuna.tsinghua.edu.cn/simple
```

- `pymysql`：Django 4.2 连接 MySQL 的驱动
- `dj-database-url`：解析 `DATABASE_URL` 连接串
- `backend/config/__init__.py` 已写入 `pymysql.install_as_MySQLdb()`（Django 连 MySQL 必需）

## 三、创建数据库与账号

```sql
-- MySQL 8.0
CREATE DATABASE customer_crawler DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'crawler'@'%' IDENTIFIED BY '你的强密码';
GRANT ALL PRIVILEGES ON customer_crawler.* TO 'crawler'@'%';
FLUSH PRIVILEGES;
```

## 四、初始化表结构（两种方式二选一）

### 方式 A：纯 SQL（推荐，含全部业务表 + 演示数据）

```bash
mysql -u crawler -p customer_crawler < scripts/init.sql          # 20 张表（商业化/B2B/短视频/合规）
mysql -u crawler -p customer_crawler < scripts/init_distribution.sql  # 补 7 张表（分销 + 推广员关注行业）
```

### 方式 B：Django 迁移（只建 Django 模型表，无演示数据）

```bash
set DATABASE_URL=mysql://crawler:密码@127.0.0.1:3306/customer_crawler
python manage.py migrate
python manage.py createsuperuser
```

## 五、启动后端

```powershell
# PowerShell（本机）
$env:DATABASE_URL = "mysql://crawler:密码@127.0.0.1:3306/customer_crawler"
$env:DJANGO_DEBUG = "1"          # 生产设 "0"
$env:DJANGO_ALLOWED_HOSTS = "你的域名或IP"
python manage.py runserver 0.0.0.0:8080
```

Linux/容器环境等价：

```bash
export DATABASE_URL="mysql://crawler:密码@127.0.0.1:3306/customer_crawler"
python manage.py runserver 0.0.0.0:8080
```

## 六、前端对接真实后端

前端 `frontend/src/api/index.js` 自动判断：

- GitHub Pages（`.github.io`）→ **mock 模式**（演示数据，无需后端）
- 本地 `localhost` 且 localStorage 无 `api_base` → mock 模式
- 其他（生产服务器）→ **real 模式**，请求 `/api`，需配置反向代理

生产部署时用 Nginx 反代：

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 七、关键环境变量（backend/config/settings.py 已支持）

| 变量 | 默认 | 说明 |
|---|---|---|
| `DATABASE_URL` | 无（用 SQLite） | `mysql://user:pass@host:3306/dbname` |
| `DJANGO_SECRET_KEY` | dev-insecure... | 生产必须设置强随机值 |
| `DJANGO_DEBUG` | `1` | 生产设 `0` |
| `DJANGO_ALLOWED_HOSTS` | `*` | 逗号分隔域名 |
| `JWT_SECRET` / `JWT_EXPIRES` | 默认 | JWT 签名密钥/过期秒数 |

## 八、验证

```bash
# 健康检查
python manage.py check
# 登录测试
curl -X POST http://127.0.0.1:8080/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123456\"}"
# 行业导航（需带 token）
curl -H "Authorization: Bearer <token>" http://127.0.0.1:8080/api/keywords/industry-nav
# 行业树（法律行业 drill-down）
curl -H "Authorization: Bearer <token>" "http://127.0.0.1:8080/api/keywords/industry-tree?industry=%E6%B3%95%E5%BE%8B%E8%A1%8C%E4%B8%9A"
```

## 九、当前状态（2026-08-01）

- ✅ 依赖已装（pymysql/dj-database-url）
- ✅ `config/__init__.py` MySQL 补丁
- ✅ `scripts/init.sql`（20 表）+ `scripts/init_distribution.sql`（7 表）
- ✅ 后端 industry-nav/tree/leads/regions 对齐前端（18/18 测试通过）
- ⏳ 待用户提供：MySQL 服务器地址/账号，或部署到云服务器后设置 `DATABASE_URL`
