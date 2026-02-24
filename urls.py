from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # =========================
    # 1. 認証・アカウント系
    # =========================
    path('login/', views.index, name='login'),            # ログイン画面
    path('logout/', views.logout_view, name='logout'),    # ログアウト
    path('home/', views.home, name='home'),                # ホーム画面
    path('signup/', views.signup, name='signup'),         # 新規登録
    path('avatar/', views.avatar_edit, name='avatar_edit'), # アバター編集
    path('check-username/', views.check_username, name='check_username'), # Ajax

    # =========================
    # 2. カレンダー・予定管理
    # =========================
    path('calendar/', views.calendar_view, name='calendar'),
    # 相手側の既存名
    path('calendar/view/', views.calendar_view, name='calendar_view'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='index_with_date'),
    # あなたの追加・修正用
    path('calendar/add/', views.add_schedule, name='add_schedule'),
    path('calendar/detail/<int:pk>/', views.schedule_detail, name='detail'),
    path('calendar/update/', views.update_schedule, name='update_schedule'),
    path('calendar/delete/<int:pk>/', views.delete_schedule, name='delete_schedule'),
    path('delete_task/<int:pk>/', views.delete_and_gain_exp, name='delete_task'), # タスク削除と経験値獲得の統合

    # =========================
    # 3. パスワード再設定
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

    # =========================
    # 4. ショップ機能
    # =========================
    path('shop/', views.shop_view, name='avatar_shop'),
    path('shop/buy/', views.buy_item, name='buy_item'),
    path('gain-exp/', views.gain_exp_api, name='gain_exp_api'),

    # =========================
    # 5. ミッション・ニュース機能 (あなたの追加分)
    # =========================
    # ミッション一覧
    path('missions/', views.mission_list, name='mission_list'),
    
    # デイリーニュース画面
    path('news/', views.news_view, name='news_view'),

    # ヘルプ閲覧ミッション（Ajax用）
    path('complete-help/', views.complete_help, name='complete_help'),

    # 称号・報酬の受け取り用
    path('claim-reward/<int:progress_id>/', views.claim_mission_reward, name='claim_reward'),
]
