"""
Production settings for JobApply AI.
"""
from .base import *
import dj_database_url
from decouple import config

DEBUG = False

# Database - Railway PostgreSQL
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Security
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=lambda v: [h.strip() for h in v.split(",") if h.strip()])

# CORS
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=lambda v: [h.strip() for h in v.split(",") if h.strip()])
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=lambda v: [h.strip() for h in v.split(",") if h.strip()])

# SSL/Proxy (Railway terminates TLS)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# WhiteNoise for static files
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage"
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# Media files on Railway volume (persistent)
MEDIA_ROOT = config("MEDIA_ROOT", default="/data/media")
MEDIA_URL = "/media/"

# Email
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@jobapply.ai")

# Brevo fallback
BREVO_SMTP_HOST = config("BREVO_SMTP_HOST", default="smtp-relay.brevo.com")
BREVO_SMTP_PORT = config("BREVO_SMTP_PORT", default=587, cast=int)
BREVO_SMTP_USER = config("BREVO_SMTP_USER", default="")
BREVO_SMTP_PASSWORD = config("BREVO_SMTP_PASSWORD", default="")

# Encryption key for user SMTP passwords
FIELD_ENCRYPTION_KEY = config("FIELD_ENCRYPTION_KEY")

# AI
GEMINI_API_KEY = config("GEMINI_API_KEY", default="")
GROQ_API_KEY = config("GROQ_API_KEY", default="")
DEFAULT_LLM_PROVIDER = config("DEFAULT_LLM_PROVIDER", default="gemini")

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
