from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.views import PasswordResetView

from .forms import SignUpForm


# =========================
# ログイン画面
# =========================
def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'users/login.html', {
                'error': 'ユーザー名かパスワードが間違っています'
            })

    return render(request, 'users/login.html')


# =========================
# ホーム画面
# =========================
def home(request):
    return render(request, 'users/home.html')


# =========================
# 新規登録（自動ログイン）
# =========================
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # パスワードをハッシュ化して保存
            user.set_password(form.cleaned_data['password'])
            user.save()

            # 登録後すぐログイン
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'users/signup.html', {'form': form})


# =========================
# ユーザー名重複チェック（Ajax）
# =========================
def check_username(request):
    username = request.GET.get("username", "").strip()
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({"exists": exists})


# =========================
# パスワード再設定（ユーザー名をセッションに保存）
# =========================
class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    success_url = '/password_reset/done/'

    def form_valid(self, form):
        email = form.cleaned_data['email']

        try:
            user = User.objects.get(email=email)
            # ★ ユーザー名を一時保存
            self.request.session['reset_username'] = user.username
        except User.DoesNotExist:
            self.request.session['reset_username'] = None

        return super().form_valid(form)
