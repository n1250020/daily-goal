import calendar
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.decorators import login_required
import feedparser # 追記

# モデルと関数のインポート（あなたの作成したモデルと関数を追加）
from .models import Avatar, Schedule, AvatarItem, UserMissionProgress, Mission, update_mission_progress, handle_auto_missions
from .forms import SignUpForm

from webpush import send_user_notification

# 共通のリダイレクト先
REDIRECT_URL = '/calendar/'

# =========================
# 認証系 (ログイン・新規登録)
# =========================

def index(request):
    """ログイン画面"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(REDIRECT_URL)
        else:
            return render(request, 'users/login.html', {
                'error': 'ユーザー名かパスワードが間違っています'
            })
    return render(request, 'users/login.html')

def home(request):
    """ホーム画面の交通整理"""
    if request.user.is_authenticated:
        return redirect(REDIRECT_URL)
    return redirect('login')

def signup(request):
    """新規登録"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Avatar.objects.get_or_create(user=user) # あなたのロジック
            login(request, user)
            return redirect(REDIRECT_URL)
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})

@login_required
def logout_view(request):
    """ログアウト処理"""
    logout(request)
    return redirect('login')

# =========================
# カレンダー・予定管理
# =========================

@login_required
def calendar_view(request, year=None, month=None):
    # ★あなたの追加機能：自動ミッション（ログイン系）の実行
    handle_auto_missions(request.user, 'login')

    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    if month == 1: prev_year, prev_month = year - 1, 12
    else: prev_year, prev_month = year, month - 1
    if month == 12: next_year, next_month = year + 1, 1
    else: next_year, next_month = year, month + 1

    # 相手側の経験値計算を呼び出す
    current_lv, display_exp = get_user_stats(request.user)

    schedule_queryset = Schedule.objects.filter(
        user=request.user, 
        date__year=year, 
        date__month=month
    )

    schedules = {}
    for s in schedule_queryset:
        day = s.date.day
        if day not in schedules:
            schedules[day] = []
        schedules[day].append(s)

    context = {
        'calendar': month_days,
        'year': year, 'month': month, 'today': today,
        'prev_year': prev_year, 'prev_month': prev_month,
        'next_year': next_year, 'next_month': next_month,
        'schedules': schedules,
        'current_lv': current_lv,
        'display_exp': display_exp,
        'avatar': Avatar.objects.filter(user=request.user).first(), # あなたのロジック
    }
    return render(request, 'users/calendar.html', context)

@login_required
def add_schedule(request):
    """予定を新規保存し、通知を送る"""
    if request.method == 'POST':
        title = request.POST.get('title')
        detail_text = request.POST.get('detail')
        date_str = request.POST.get('date')
        level = int(request.POST.get('level', 1))

        if title and date_str:
            Schedule.objects.create(
                user=request.user,
                title=title,
                description=detail_text,
                date=date_str,
                level=level
            )
            group_name = f"user_{request.user.id}"
            payload = {
                "head": "新しい予定を追加しました！",
                "body": f"タイトル: {title}\n日付: {date_str}",
                "icon": "/static/images/icon.png",
                "url": "/calendar/"
            }
            try:
                send_user_notification(user=request.user, payload=payload, ttl=1000)
            except Exception as e:
                print(f"通知エラー詳細: {e}")

    return redirect('calendar')

@login_required
def schedule_detail(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    return render(request, 'users/schedule_detail.html', {'schedule': schedule})

@login_required
def update_schedule(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('id')
        schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
        schedule.title = request.POST.get('title')
        schedule.description = request.POST.get('detail') 
        schedule.level = request.POST.get('level', 1)
        schedule.save()
    return redirect('calendar')

@login_required
def delete_schedule(request, pk):
    if request.method == 'POST':
        schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
        schedule.delete()
    return redirect('calendar')

# =========================
# アバター編集 (あなたのロジックで統合)
# =========================
@login_required
def avatar_edit(request):
    avatar, _ = Avatar.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        avatar.face_type = request.POST.get('face_type', '0')
        avatar.frame_type = request.POST.get('frame_type', '0')
        avatar.back_type = request.POST.get('back_type', '0')
        avatar.clothes_type = request.POST.get('clothes_type', '0')
        # あなたの追加：称号セット
        avatar.current_title = request.POST.get('current_title', avatar.current_title)
        avatar.save()
        
        # あなたの追加：ミッション進捗
        update_mission_progress(request.user, "好印象の魔法使い")
        return redirect('avatar_edit')

    owned_items = avatar.owned_items.all()
    return render(request, 'users/avatar_edit.html', {
        'avatar': avatar,
        'owned_items': owned_items,
    })

# =========================
# ショップ画面 (統合)
# =========================
@login_required
def shop_view(request):
    avatar, _ = Avatar.objects.get_or_create(user=request.user)
    owned_items = avatar.owned_items.all()
    unowned_items = AvatarItem.objects.exclude(id__in=owned_items.values_list('id', flat=True))
    return render(request, 'users/shop.html', {
        'avatar': avatar,
        'unowned_items': unowned_items,
        'owned_items': owned_items,
    })

@login_required
def buy_item(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        item = get_object_or_404(AvatarItem, id=item_id)
        avatar = Avatar.objects.get(user=request.user)

        if item in avatar.owned_items.all():
            return redirect('avatar_shop')

        if avatar.points >= item.price:
            avatar.points -= item.price
            avatar.owned_items.add(item)
            avatar.save()
            # あなたの追加：ミッション進捗
            update_mission_progress(request.user, "自分磨きの天才")
    return redirect('avatar_shop')

# =========================
# ニュース (あなたの新規追加)
# =========================
@login_required
def news_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        mission_name = "ニュースチェック"
        mission = Mission.objects.filter(title=mission_name).first()
        already_completed = False
        if mission:
            prog = UserMissionProgress.objects.filter(user=request.user, mission=mission).first()
            if prog and prog.is_completed:
                already_completed = True

        update_mission_progress(request.user, mission_name)
        update_mission_progress(request.user, "物知り博士")
        update_mission_progress(request.user, "一目置かれる実力者")

        # 頼れるリーダーの判定
        daily_progs = UserMissionProgress.objects.filter(user=request.user, mission__mission_type='daily')
        if daily_progs.exists() and all(p.is_completed for p in daily_progs):
            handle_auto_missions(request.user, 'all_cleared')

        new_mission_cleared = False
        if mission:
            prog = UserMissionProgress.objects.filter(user=request.user, mission=mission).first()
            if not already_completed and prog and prog.is_completed:
                new_mission_cleared = True
        return JsonResponse({'status': 'success', 'mission_cleared': new_mission_cleared})

    rss_url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ja&gl=JP&ceid=JP:ja"
    feed = feedparser.parse(rss_url)
    news_items = [{'title': e.title, 'link': e.link, 'published': e.published, 'source': e.source.title if hasattr(e, 'source') else "不明"} for e in feed.entries[:8]]
    mission = Mission.objects.filter(title="ニュースチェック").first()
    mission_cleared = False
    if mission:
        user_mission = UserMissionProgress.objects.filter(user=request.user, mission=mission).first()
        if user_mission and user_mission.is_completed:
            mission_cleared = True

    return render(request, 'users/news.html', {
        'news_items': news_items,
        'avatar': Avatar.objects.filter(user=request.user).first(),
        'mission_cleared': mission_cleared,
    })

# =========================
# ミッション一覧 (あなたの新規追加)
# =========================
@login_required
def mission_list(request):
    avatar = Avatar.objects.filter(user=request.user).first()
    today = date.today()
    daily_progs = UserMissionProgress.objects.filter(user=request.user, mission__mission_type='daily')
    if daily_progs.exists() and all(p.is_completed and p.last_updated == today for p in daily_progs):
        handle_auto_missions(request.user, 'all_cleared')

    all_missions = Mission.objects.all()
    for m in all_missions:
        prog, _ = UserMissionProgress.objects.get_or_create(user=request.user, mission=m)
        if m.mission_type == 'daily' and prog.last_updated < today:
            prog.is_completed = False
            prog.current_count = 0
            prog.save()
    
    progress_list = UserMissionProgress.objects.filter(user=request.user).select_related('mission')
    return render(request, 'users/mission_list.html', {
        'avatar': avatar,
        'daily_missions': progress_list.filter(mission__mission_type='daily'),
        'honor_missions': progress_list.filter(mission__mission_type='honor'),
    })

@login_required
def claim_mission_reward(request, progress_id):
    progress = get_object_or_404(UserMissionProgress, id=progress_id, user=request.user)
    if progress.is_completed and not progress.is_reward_received:
        mission = progress.mission
        avatar, _ = Avatar.objects.get_or_create(user=request.user)
        if mission.title_reward:
            avatar.current_title = mission.title_reward
            avatar.save()
        progress.is_reward_received = True
        progress.save()
        return JsonResponse({'status': 'success', 'message': f'称号【{mission.title_reward}】を獲得しました！'})
    return JsonResponse({'status': 'error'}, status=400)

# =========================
# 共通ロジック：経験値・レベル (相手側を維持)
# =========================
def get_user_stats(user):
    all_schedules = Schedule.objects.filter(user=user)
    schedule_exp = sum(s.level * 10 for s in all_schedules)
    avatar, _ = Avatar.objects.get_or_create(user=user)
    extra_exp = avatar.points
    total_exp = schedule_exp + extra_exp
    current_lv = (total_exp // 100) + 1
    display_exp = total_exp % 100
    return current_lv, display_exp

# 相手側の既存APIを維持
def gain_exp_api(request):
    if request.method == 'POST':
        avatar, _ = Avatar.objects.get_or_create(user=request.user)
        avatar.points += 20 
        avatar.save()
        current_lv, display_exp = get_user_stats(request.user)
        return JsonResponse({'status': 'success', 'new_exp': display_exp, 'level': current_lv})

@login_required
def complete_help(request): # あなたの修正分
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        update_mission_progress(request.user, "準備のプロ")
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def check_username(request):
    username = request.GET.get("username", "").strip()
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({"exists": exists})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    success_url = '/password_reset/done/'
    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            self.request.session['reset_username'] = user.username
        except User.DoesNotExist:
            self.request.session['reset_username'] = None
        return super().form_valid(form)

# =========================
# ★不足していた関数を追加 (相手側urls.py用)
# =========================
@login_required
def delete_and_gain_exp(request, pk):
    """タスクを削除し、経験値を獲得する"""
    if request.method == 'POST':
        schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
        # 経験値計算（一例：スケジュールレベル×10）
        gain = schedule.level * 10
        avatar, _ = Avatar.objects.get_or_create(user=request.user)
        avatar.points += gain
        avatar.save()
        
        schedule.delete()
        
        # ミッション判定（全クリア判定）
        handle_auto_missions(request.user, 'all_cleared')
        
        return JsonResponse({'status': 'success', 'points': avatar.points})
    return JsonResponse({'status': 'error'}, status=400)
