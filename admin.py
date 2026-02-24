from django.contrib import admin
from .models import Avatar, AvatarItem, Mission, UserMissionProgress, Schedule
from .models_remote import Notifications

# --- 1. カレンダー・予定管理 (相手側設定を維持) ---
admin.site.register(Schedule)

# --- 2. 既存の Notifications 設定 (相手側設定を維持) ---
@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'message', 'scheduled_at', 'is_sent')
    search_fields = ('message',)
    list_filter = ('is_sent', 'scheduled_at')

# --- 3. Avatar（現在の装備・ステータス）の設定 (統合・追記) ---
@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    # あなたの追加した current_title, level を含めつつ、相手の face_type 等も確認できる表示
    list_display = ('user', 'current_title', 'level', 'points', 'face_type', 'updated_at')
    # ユーザー名で検索できるようにする
    search_fields = ('user__username',)

# --- 4. AvatarItem（ショップの商品）の設定 (詳細設定を追記) ---
@admin.register(AvatarItem)
class AvatarItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'image_id', 'price')
    list_filter = ('category',)
    search_fields = ('name',)

# --- 5. Mission（ミッションのマスターデータ）の設定 (あなたの新規追記) ---
@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'mission_type', 'required_count', 'exp_reward')
    list_filter = ('mission_type',)
    search_fields = ('title',)

# --- 6. UserMissionProgress（ユーザーごとの進捗）の設定 (あなたの新規追記) ---
@admin.register(UserMissionProgress)
class UserMissionProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'mission', 'current_count', 'is_completed', 'last_updated')
    list_filter = ('is_completed', 'mission__mission_type')
    search_fields = ('user__username', 'mission__title')
