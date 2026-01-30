from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="パスワード"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="パスワード（確認）"
    )

    class Meta:
        model = User
        fields = ['username', 'email']  # password系は含めない
        labels = {
            'username': 'ユーザー名',
            'email': 'メールアドレス',
        }

    # ユーザー名チェック
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("ユーザー名を入力してください")
        if User.objects.filter(username=username).exists():
            raise ValidationError("このユーザー名は既に使用されています")
        return username

    # メールアドレス（任意）
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("このメールアドレスは既に登録されています")
        return email

    # パスワード強度チェック（★日本語完全拒否入り）
    def clean_password(self):
        password = self.cleaned_data.get("password")

        if not password:
            raise ValidationError("パスワードを入力してください")

        # 8文字以上
        if len(password) < 8:
            raise ValidationError("パスワードは8文字以上で入力してください")

        # 英字を含む
        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("パスワードには英字を含めてください")

        # 数字を含む
        if not re.search(r"[0-9]", password):
            raise ValidationError("パスワードには数字を含めてください")

        # ★ 日本語・全角文字を完全拒否
        if re.search(r"[^\x00-\x7F]", password):
            raise ValidationError("日本語・全角文字は使用できません")

        return password

    # 確認用パスワード一致チェック
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "パスワードが一致しません")

        return cleaned_data

