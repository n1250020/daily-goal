from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta

# --- 1. カレンダー・予定管理 (相手側) ---
class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    level = models.IntegerField(default=1)  # 経験値計算用 (1, 2, 3)
    is_done = models.BooleanField(default=False)  # 完了フラグ
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# --- 2. アイテムマスタ (共通) ---
class AvatarItem(models.Model):
    CATEGORY_CHOICES = [
        ('face', '顔・表情'),
        ('frame', 'フレーム'),
        ('back', '背景'),
        ('clothes', '服'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image_id = models.IntegerField()  # ファイル名の番号
    price = models.IntegerField(default=0)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name}"

# --- 3. ミッションの定義 (あなたの追加) ---
class Mission(models.Model):
    MISSION_TYPES = [
        ('daily', 'デイリー'),
        ('normal', '通常'),
        ('honor', '称号'),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    mission_type = models.CharField(max_length=10, choices=MISSION_TYPES)
    required_count = models.IntegerField(default=1)  # クリアに必要な回数
    exp_reward = models.IntegerField(default=20)    # 獲得できる経験値量
    title_reward = models.CharField(max_length=50, blank=True, null=True) # クリアで貰える称号名

    def __str__(self):
        return self.title

# --- 4. ユーザーのアバター・所持データ (統合) ---
class Avatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # あなたの追加: 名前
    name = models.CharField(max_length=100, blank=True)
    
    # 相手側の設定を維持: 全て default=0 に統一
    face_type = models.IntegerField(default=0)
    eye_type = models.IntegerField(default=0)
    mouth_type = models.IntegerField(default=0)
    clothes_type = models.IntegerField(default=0)
    back_type = models.IntegerField(default=0)
    frame_type = models.IntegerField(default=0)

    # 購入済みのアイテムを管理
    owned_items = models.ManyToManyField(AvatarItem, blank=True)
    
    # 所持ポイント
    points = models.IntegerField(default=0) 

    # あなたの追加: 称号・レベル・経験値
    current_title = models.CharField(max_length=50, default="新米")
    level = models.IntegerField(default=1)
    exp = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    # あなたの追加: 連続ログイン判定用
    last_login_date = models.DateField(null=True, blank=True)

    # あなたの追加: 自動名前設定ロジック
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.user.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Avatar"

# --- 5. ユーザーごとのミッション進捗 (あなたの追加) ---
class UserMissionProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    current_count = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    is_reward_received = models.BooleanField(default=False)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.mission.title}"

# --- 6. ミッション更新ロジック (あなたの関数) ---
def update_mission_progress(user, mission_title):
    try:
        mission = Mission.objects.filter(title__iexact=mission_title.strip()).first()
        if not mission:
            print(f"DEBUG: Mission '{mission_title}' not found.")
            return

        progress, created = UserMissionProgress.objects.get_or_create(
            user=user, 
            mission=mission
        )

        # リセット判定
        if not created and mission.mission_type == 'daily' and progress.last_updated < date.today():
            progress.current_count = 0
            progress.is_completed = False
            progress.is_reward_received = False

        if progress.is_reward_received:
            return

        avatar, _ = Avatar.objects.get_or_create(user=user)
        
        if mission_title == "一目置かれる実力者":
            progress.current_count = avatar.points
        else:
            if not progress.is_completed:
                progress.current_count += 1

        if not progress.is_completed:
            if progress.current_count >= mission.required_count:
                progress.is_completed = True
                
                if mission.title_reward:
                    avatar.current_title = mission.title_reward
                    avatar.save()
        
        progress.save()
        
    except Exception as e:
        print(f"Mission update error: {e}")

# --- 7. 自動ミッション判定ロジック (あなたの関数) ---
def handle_auto_missions(user, event_type):
    """
    event_type: 'login' または 'all_cleared'
    """
    avatar, _ = Avatar.objects.get_or_create(user=user)
    today = date.today()

    if event_type == 'login':
        if avatar.last_login_date != today:
            update_mission_progress(user, "努力の天才")
            
            if avatar.last_login_date == today - timedelta(days=1):
                update_mission_progress(user, "心のタフ自慢")
            else:
                try:
                    tough_mission = Mission.objects.get(title="心のタフ自慢")
                    prog_tough, _ = UserMissionProgress.objects.get_or_create(
                        user=user, 
                        mission=tough_mission
                    )
                    if not prog_tough.is_completed:
                        prog_tough.current_count = 1
                        prog_tough.save()
                except Mission.DoesNotExist:
                    print("DEBUG: '心のタフ自慢' ミッションがDBに登録されていません")

            avatar.last_login_date = today
            avatar.save()

    elif event_type == 'all_cleared':
        try:
            leader_mission = Mission.objects.get(title="頼れるリーダー")
            # 内部で重複チェックを行う update_mission_progress を利用
            update_mission_progress(user, "頼れるリーダー")
            
        except Mission.DoesNotExist:
            print("DEBUG: '頼れるリーダー' ミッションがDBに登録されていません")
