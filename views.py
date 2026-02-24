import calendar
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.decorators import login_required
import feedparser

# モデルと関数のインポート
from .models import Avatar, AvatarItem, UserMissionProgress, Mission, update_mission_progress 
from .forms import SignUpForm

# --- 認証・トップページ系 ---
def index(request):
    if request.user.is_authenticated:
        return redirect('calendar_view') 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('calendar_view')
        else:
            return render(request, 'users/login.html', {'error': 'ユーザー名かパスワードが間違っています'})
    return render(request, 'users/login.html')

def home(request):
    """urls.pyのエラーを修正するために復活させた関数"""
    return redirect('calendar_view') if request.user.is_authenticated else redirect('login')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Avatar.objects.get_or_create(user=user)
            login(request, user)
            return redirect('calendar_view')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})

# --- アバター編集 ---
@login_required
def avatar_edit(request):
    avatar, _ = Avatar.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        avatar.face_type = request.POST.get('face_type', '0')
        avatar.frame_type = request.POST.get('frame_type', '0')
        avatar.back_type = request.POST.get('back_type', '0')
        avatar.clothes_type = request.POST.get('clothes_type', '0')
        
        # ★ここを追記：HTMLから送られてきた称号をセットする
        avatar.current_title = request.POST.get('current_title', avatar.current_title)
        
        avatar.save()
        
        # 【修正】名前を合わせました
        update_mission_progress(request.user, "好印象の魔法使い")
        
        return redirect('avatar_edit')
    return render(request, 'users/avatar_edit.html', {'avatar': avatar, 'owned_items': avatar.owned_items.all()})

# --- カレンダー表示 ---
@login_required
def calendar_view(request, year=None, month=None):
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)
    
    if month == 1: prev_year, prev_month = year - 1, 12
    else: prev_year, prev_month = year, month - 1
    if month == 12: next_year, next_month = year + 1, 1
    else: next_year, next_month = year, month + 1

    return render(request, 'users/calendar.html', {
        'calendar': month_days, 'year': year, 'month': month, 'today': today,
        'prev_year': prev_year, 'prev_month': prev_month,
        'next_year': next_year, 'next_month': next_month,
        'avatar': Avatar.objects.filter(user=request.user).first(),
    })

# --- ショップ ---
@login_required
def shop_view(request):
    avatar, _ = Avatar.objects.get_or_create(user=request.user)
    owned_items = avatar.owned_items.all()
    unowned_items = AvatarItem.objects.exclude(id__in=owned_items.values_list('id', flat=True))
    return render(request, 'users/shop.html', {'avatar': avatar, 'unowned_items': unowned_items, 'owned_items': owned_items})

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
            
            # 【修正】名前を合わせました
            update_mission_progress(request.user, "自分磨きの天才")
            
    return redirect('avatar_shop')

# --- ニュース ---
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

        # 【修正】名前を合わせました
        update_mission_progress(request.user, mission_name)
        update_mission_progress(request.user, "物知り博士")
        update_mission_progress(request.user, "一目置かれる実力者")

        new_mission_cleared = False
        if mission:
            prog = UserMissionProgress.objects.filter(user=request.user, mission=mission).first()
            if not already_completed and prog and prog.is_completed:
                new_mission_cleared = True

        return JsonResponse({
            'status': 'success',
            'mission_cleared': new_mission_cleared
        })

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

# --- ミッション一覧 ---
@login_required
def mission_list(request):
    avatar = Avatar.objects.filter(user=request.user).first()
    today = date.today()
    
    # 【修正】名前を合わせました
    target_mission = Mission.objects.filter(title="努力の天才").first()
    if target_mission:
        prog_total, _ = UserMissionProgress.objects.get_or_create(
            user=request.user, 
            mission=target_mission
        )
        if prog_total.last_updated < today:
            update_mission_progress(request.user, "努力の天才")
            update_mission_progress(request.user, "心のタフ自慢")
    
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

# --- 報酬受け取り ---
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

# --- その他共通 ---
@login_required
def complete_help(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # 【修正】名前を合わせました
        update_mission_progress(request.user, "準備のプロ")
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def add_schedule(request): return redirect('calendar_view')
@login_required
def schedule_detail(request, pk): return JsonResponse({"message": "準備中"})

def check_username(request):
    return JsonResponse({"exists": User.objects.filter(username=request.GET.get("username", "").strip()).exists()})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    success_url = '/password_reset/done/'
