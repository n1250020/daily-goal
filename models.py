from django.db import models
from django.contrib.auth.models import User

# --- ショップで売るアイテムそのもののデータ ---
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

# --- 現在の装備と所持状況を管理 ---
class Avatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # 全て default=0 に統一。これで「未所持・未設定」が正しく扱えます
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

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Avatar"
