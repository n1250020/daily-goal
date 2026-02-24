from django.db import models
from django.contrib.auth.models import User
from datetime import date

# --- 既存のモデル ---
class AvatarItem(models.Model):
    CATEGORY_CHOICES = [
        ('face', '顔・表情'),
        ('frame', 'フレーム'),
        ('back', '背景'),
        ('clothes', '服'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image_id = models.IntegerField()
    price = models.IntegerField(default=0)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name}"

# --- ミッションの定義 ---
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

# --- 修正後の Avatar モデル ---
class Avatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    face_type = models.IntegerField(default=0)
    eye_type = models.IntegerField(default=0)
    mouth_type = models.IntegerField(default=0)
    clothes_type = models.IntegerField(default=0)
    back_type = models.IntegerField(default=0)
    frame_type = models.IntegerField(default=0)
    owned_items = models.ManyToManyField(AvatarItem, blank=True)
    points = models.IntegerField(default=0) 

    current_title = models.CharField(max_length=50, default="新米")
    level = models.IntegerField(default=1)
    exp = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.user.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}'s Avatar"

# --- ユーザーごとのミッション進捗 ---
class UserMissionProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    current_count = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    is_reward_received = models.BooleanField(default=False)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.mission.title}"

# --- ミッション更新ロジック（修正版） ---
def update_mission_progress(user, mission_title):
    try:
        # タイトルで検索（管理画面の名前に合わせる）
        mission = Mission.objects.filter(title__iexact=mission_title.strip()).first()
        if not mission:
            print(f"DEBUG: Mission '{mission_title}' not found.")
            return

        progress, created = UserMissionProgress.objects.get_or_create(
            user=user, 
            mission=mission
        )

        # デイリーリセット判定
        if mission.mission_type == 'daily' and progress.last_updated < date.today():
            progress.current_count = 0
            progress.is_completed = False
            progress.is_reward_received = False

        if progress.is_reward_received:
            return

        avatar, _ = Avatar.objects.get_or_create(user=user)
        
        # 【修正点】条件分岐の名前を「称号」なしの名前に合わせる
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
