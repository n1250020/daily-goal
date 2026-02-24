"""
Django settings for testlogin project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# =========================
# Base
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# .env を読み込む
load_dotenv()

# =========================
# SECURITY
# =========================
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dummy-key-for-now')
DEBUG = True

# 自分のホスト名やIPを許可 (相手側の設定をすべて維持)
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'PC1250020',
    '10.17.5.116',
    '*', # 開発中のみ：どのIPからのアクセスも許可する設定
]

# =========================
# Application definition
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',   # アプリケーション
    'webpush', # 相手側のWebpush機能
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'testlogin.urls'

# =========================
# Templates
# =========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # あなたのミッション画面などのHTMLを読み込むために追加
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'testlogin.wsgi.application'

# =========================
# Database
# =========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =========================
# Password validation
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================
# Internationalization
# =========================
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

# =========================
# Static files
# =========================
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# アバター画像やCSSを正しく配信するために追加
STATIC_ROOT = BASE_DIR / "staticfiles"

# =========================
# Default primary key field
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================
# 認証・ログイン関連
# =========================
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

# ログイン後のリダイレクト先（相手側の設定を維持）
LOGIN_REDIRECT_URL = 'http://10.17.7.127:8000/'

# =========================
# パスワード再設定設定
# =========================
# メール内のURLドメイン
DOMAIN = os.getenv('DOMAIN', '127.0.0.1:8000')
SITE_DOMAIN = DOMAIN
PASSWORD_RESET_TIMEOUT = 3600  # 1時間有効

# =========================
# メール送信設定 (Gmail SMTP)
# =========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# 送信元の表示設定
DEFAULT_FROM_EMAIL = f'Daily Goal <{EMAIL_HOST_USER}>'
