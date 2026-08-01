"""
客户大数据爬虫开发程序 - Django 配置
"""
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-secret-key-change-in-production")

DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 第三方
    "rest_framework",
    "corsheaders",
    # 业务应用
    "apps.users",
    "apps.keywords",
    "apps.crawler",
    "apps.leads",
    "apps.tasks",
    "apps.analytics",
    "apps.stats",
    "apps.core",
    "apps.biz",
    "apps.crm",
    "apps.monitor",
    "apps.commerce",
    "apps.distribution",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 自定义：合规操作日志
    "apps.core.middleware.ComplianceLogMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# 数据库：默认 SQLite（开箱即用）；生产环境通过 DATABASE_URL 切换 MySQL/PostgreSQL
if os.getenv("DATABASE_URL"):
    import dj_database_url

    DATABASES = {"default": dj_database_url.config(default=os.getenv("DATABASE_URL"))}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# 认证
AUTH_USER_MODEL = "users.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------- REST Framework ----------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.users.middleware.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
}

# ---------- JWT ----------
JWT_SECRET = os.getenv("JWT_SECRET", SECRET_KEY)
JWT_ALGORITHM = "HS256"
JWT_EXPIRES = timedelta(hours=24)

# ---------- CORS ----------
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL", "1") == "1"
CORS_ALLOW_CREDENTIALS = True

# ---------- Redis / Celery（可选：无 Redis 时降级为进程内队列） ----------
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "0") == "1"

# ---------- 爬虫风控参数 ----------
CRAWLER_SETTINGS = {
    "default_min_interval": float(os.getenv("CRAWLER_MIN_INTERVAL", "3")),  # 每平台最小请求间隔（秒）
    "max_rpm": int(os.getenv("CRAWLER_MAX_RPM", "20")),  # 每平台每分钟最大请求数
    "max_retries": 3,
    "retry_backoff": 5.0,  # 指数退避基数（秒）
    "ban_cooldown": 300,  # 触发风控后冷却（秒）
    "proxy_enabled": os.getenv("CRAWLER_PROXY_ENABLED", "0") == "1",
}

# ---------- 数据合规 ----------
COMPLIANCE = {
    "data_retention_days": int(os.getenv("DATA_RETENTION_DAYS", "30")),  # 30 天自动清理
    "log_retention_days": 90,
}

# ---------- 意向打分权重 ----------
INTENT_SCORING = {
    "content_length": 0.1,
    "keyword_match": 0.4,
    "sentiment": 0.3,
    "interaction": 0.2,
}

# 高德地图（用于热力图聚合与逆地理编码；无 Key 时仅展示点位）

# ---------- 官方开放 API 凭证 (合规采集) ----------
# 在各平台开放平台申请开发者权限后, 将凭证填入 .env 或此处:
#   抖音:    DOUYIN_CLIENT_KEY / DOUYIN_CLIENT_SECRET  (open.douyin.com)
#   小红书:  XHS_APP_ID / XHS_APP_SECRET               (专业号开放平台)
#   快手:    KUAISHOU_APP_KEY / KUAISHOU_APP_SECRET    (open.kuaishou.com)
#   微博:    WEIBO_ACCESS_TOKEN                        (open.weibo.com)
#   知乎:    ZHIHU_TOKEN                               (合作通道)
#   贴吧:    TIEBA_COOKIE                              (无公开 API, 预留)
# 未配置凭证时自动降级为演示数据模式 (source=demo), 保证前端可运行。
OFFICIAL_API_CREDENTIALS = {
    "douyin": {"client_key": os.getenv("DOUYIN_CLIENT_KEY", ""), "client_secret": os.getenv("DOUYIN_CLIENT_SECRET", "")},
    "xiaohongshu": {"app_id": os.getenv("XHS_APP_ID", ""), "app_secret": os.getenv("XHS_APP_SECRET", "")},
    "kuaishou": {"app_key": os.getenv("KUAISHOU_APP_KEY", ""), "app_secret": os.getenv("KUAISHOU_APP_SECRET", "")},
    "weibo": {"access_token": os.getenv("WEIBO_ACCESS_TOKEN", "")},
    "zhihu": {"token": os.getenv("ZHIHU_TOKEN", "")},
    "tieba": {"token": os.getenv("TIEBA_COOKIE", "")},
}

AMAP_KEY = os.getenv("AMAP_KEY", "")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
