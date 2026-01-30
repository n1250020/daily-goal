# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # =========================
    # 通常画面
    # =========================
    path('login/', views.index, name='login'),        # ログイン画面
    path('home/', views.home, name='home'),           # ホーム画面
    path('signup/', views.signup, name='signup'),     # 新規登録

    # =========================
    # Ajax
    # =========================
    path('check-username/', views.check_username, name='check_username'),

    # =========================
    # パスワード再設定（ユーザー名保持版）
    # =========================
    path(
        'password_reset/',
        views.CustomPasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
