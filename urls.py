from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # =========================
    # 認証・ホーム
    # =========================
    # ログイン画面
    path('login/', views.index, name='login'),
    
    # ログアウト処理
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # 新規登録・ホーム
    path('signup/', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    
    # アバター編集画面
    path('avatar/', views.avatar_edit, name='avatar_edit'),

    # =========================
    # カレンダー関連
    # =========================
    path('calendar/', views.calendar_view, name='index'), 
    path('calendar/view/', views.calendar_view, name='calendar_view'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar_view'),

    # 予定操作
    path('calendar/add/', views.add_schedule, name='add_schedule'),
    path('calendar/detail/<int:pk>/', views.schedule_detail, name='detail'),

    # =========================
    # パスワード再設定・Ajax
    # =========================
    path('check-username/', views.check_username, name='check_username'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),

    # =========================
    # ショップ機能
    # =========================
    path('shop/', views.shop_view, name='avatar_shop'),
    path('shop/buy/', views.buy_item, name='buy_item'),

    # =========================
    # ミッション機能
    # =========================
    # ミッション一覧
    path('missions/', views.mission_list, name='mission_list'),
    
    # デイリーニュース画面
    path('news/', views.news_view, name='news_view'),

    # ヘルプ閲覧ミッション（Ajax用）
    # views.pyの関数名に合わせて 'complete_help_mission' から 'complete_help' に修正しました
    path('complete-help/', views.complete_help, name='complete_help'),

    # ★ここを追加：称号・報酬の受け取り用
    path('claim-reward/<int:progress_id>/', views.claim_mission_reward, name='claim_reward'),
]
