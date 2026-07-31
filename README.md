# 客户大数据智能获客平台

> 覆盖抖音 / 小红书 / 快手 / 微博 / 知乎 / 贴吧 六大平台线索采集的客户开发系统

## 在线演示

- GitHub Pages: **https://lixiu-ohye.github.io/customer-crawler/**
- 演示账号: `admin` / `admin123456`

> ⚠️ 说明：GitHub Pages 为纯静态托管，线上演示使用内置演示数据模式（Mock API）。完整功能（真实爬虫采集、AI 分析、地图热力图等）需在本地/服务器部署后端，详见下方部署指南。

## 功能总览

| 模块 | 说明 |
|------|------|
| 数据大盘 | 线索统计卡片 + ECharts 平台/意向/趋势/任务分布图表 |
| 关键词管理 | 增删改查、批量导入、AI 拓词、否定词、分组、行业地点导航自动联想 |
| 任务中心 | 六平台采集任务、进度条、启动/暂停/终止/重试、5s 轮询刷新 |
| 线索库 | 筛选、分页、详情弹窗、跳转原文、导出 xlsx、备注、拉黑 |
| 地图热力图 | 高德地图 + 省市县联动 + 热力图与点位标注 |
| AI 分析 | 需求摘要、语义正负筛查、话术生成、批量重筛 |
| 会员中心 | 个人资料、套餐权益、操作日志 |
| 合规声明 | 免责声明确认、30 天数据自动清理说明 |

## 技术架构

- **前端**: Vue 3 + Vite + Pinia + Vue Router + ECharts + Element Plus + 高德地图 JS API
- **后端**: Django 4.2 + Django REST Framework + JWT + Redis 缓存 + Celery 异步任务
- **存储**: MySQL / PostgreSQL + Redis
- **采集**: 爬虫模式 / API 模式双适配器，含风控限速、指数退避重试、数据清洗、意向打分、自动标签

## 本地部署指南

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8080
```

可选：启动定时调度（7×24 任务监控 + 30 天数据清理）

```bash
python scripts/scheduler.py
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev   # 开发模式 http://localhost:5173
npm run build # 生产构建，产物在 dist/
```

### 3. 环境变量

后端 `config/settings.py` 可配置：

- `CRAWLER_SETTINGS`：各平台风控限速参数（请求间隔、每分钟上限）
- `COMPLIANCE`：数据保留天数（默认 30 天）
- `DATABASES`：切换 MySQL/PostgreSQL

## 合规声明

本平台仅用于合法合规的商业调研与客户开发，禁止用于骚扰、诈骗、侵犯个人隐私、不正当竞争等违法用途。涉及个人信息的数据应遵守《个人信息保护法》《数据安全法》《网络安全法》。采集的数据执行 30 天自动清理。

## 项目结构

```
customer-crawler/
├── backend/                 # Django 后端
│   ├── config/              # 项目配置（settings/urls）
│   ├── apps/
│   │   ├── users/           # 用户权限（JWT）
│   │   ├── keywords/        # 关键词管理（jieba 联想、AI 拓词）
│   │   ├── crawler/         # 六平台采集（风控限速、数据清洗、意向打分）
│   │   ├── leads/           # 线索库（筛选、导出、备注、拉黑）
│   │   ├── tasks/           # 任务队列（进度、停止/续跑）
│   │   ├── stats/           # 数据统计（大盘、分布、趋势、热力图）
│   │   ├── analytics/       # AI 分析（摘要、筛查、话术、重筛）
│   │   └── core/            # 合规（日志、30天清理、免责声明）
│   └── scripts/scheduler.py # 定时调度守护
└── frontend/                # Vue3 前端
    └── src/
        ├── views/           # 8 个页面视图
        ├── api/             # axios 封装
        ├── stores/          # Pinia 状态
        └── router/          # 路由与登录守卫
```
