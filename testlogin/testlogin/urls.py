"""
URL configuration for testlogin project.

The `urlpatterns` list routes URLs to views.
For more information see:
https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 管理画面
    path('admin/', admin.site.urls),

    # users アプリ配下の URL をすべて読み込む
    # ログイン / 新規登録 / パスワード再設定 など
    path('', include('users.urls')),
]
