import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS","127.0.0.1,localhost").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "corsheaders",
    "rest_framework","exposure",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware","django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "loanserp.urls"
TEMPLATES = [{
    "BACKEND":"django.template.backends.django.DjangoTemplates",
    "DIRS":[], "APP_DIRS":True,
    "OPTIONS":{"context_processors":[
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ],},
}]
WSGI_APPLICATION = "loanserp.wsgi.application"

# DB (psycopg3)
DB_NAME = os.getenv("POSTGRES_DB","loanserp")
DB_USER = os.getenv("POSTGRES_USER","loan")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD","loanpwd")
DB_HOST = os.getenv("POSTGRES_HOST","localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT","5432"))
DATABASES = {
    "default":{
        "ENGINE":"django.db.backends.postgresql",
        "NAME":DB_NAME,"USER":DB_USER,"PASSWORD":DB_PASSWORD,"HOST":DB_HOST,"PORT":DB_PORT,
    }
}

# Cache / Redis
REDIS_URL = os.getenv("REDIS_URL","redis://localhost:6379/1")
CACHES = {
    "default":{
        "BACKEND":"django_redis.cache.RedisCache",
        "LOCATION":REDIS_URL,
        "OPTIONS":{"CLIENT_CLASS":"django_redis.client.DefaultClient"},
        "KEY_PREFIX":"loans:seo",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Static
STATIC_URL = "static/"
STATIC_ROOT = str(BASE_DIR / "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE","zh-hant")
TIME_ZONE = os.getenv("TIME_ZONE","Asia/Taipei")
USE_I18N = True
USE_TZ = True

# DRF (minimal)
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES":["rest_framework.renderers.JSONRenderer"],
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]
CORS_ALLOW_CREDENTIALS = True

# Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_TASK_TIME_LIMIT = int(os.getenv("CELERY_TASK_TIME_LIMIT","120"))
CELERY_TASK_SOFT_TIME_LIMIT = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT","90"))

# Business settings
KEYWORD_TRACK_LIST = [k.strip() for k in os.getenv(
    "KEYWORD_TRACK_LIST","貸款,貸款評估,貸款預測,貸款推薦,房屋貸款,企業貸款,個人信貸,信貸申請,信貸相關"
).split(",") if k.strip()]

NEWS_DOMAIN_WHITELIST = [d.strip() for d in os.getenv(
    "NEWS_DOMAIN_WHITELIST",
    "money.udn.com,cnyes.com,ctee.com.tw,wealth.com.tw,bnext.com.tw,businesstoday.com.tw,cmmedia.com.tw,inside.com.tw,yahoo.com,www.fsc.gov.tw,www.cbc.gov.tw,www.mof.gov.tw,law.moj.gov.tw"
).split(",") if d.strip()]

# GSC
GSC_PROPERTY_URI = os.getenv("GSC_PROPERTY_URI","sc-domain:alphaloan.co")
# Installed App OAuth
GSC_CLIENT_SECRETS_FILE = os.getenv("GSC_CLIENT_SECRETS_FILE", str(BASE_DIR / "credentials" / "client_secret.json"))
GSC_TOKEN_FILE = os.getenv("GSC_TOKEN_FILE", str(BASE_DIR / "credentials" / "token.json"))
GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
