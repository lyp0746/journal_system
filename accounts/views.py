# accounts/views.py  
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


def register_view(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！欢迎加入上海理工大学学报投审稿系统。')
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """用户登录视图"""
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'欢迎回来，{user.username}！')

            # 获取next参数，如果有则重定向到该URL  
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """用户登出视图"""
    logout(request)
    messages.info(request, '您已成功退出登录。')
    return redirect('home')


@login_required
def profile_view(request):
    """用户个人资料视图"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料更新成功！')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# accounts/views.py (添加以下代码)
from django.http import JsonResponse
from .models import Notification


@login_required
def notification_list(request):
    """用户通知列表"""
    notifications = Notification.objects.filter(user=request.user)

    # 标记为已读
    if request.GET.get('mark_all_read'):
        notifications.update(is_read=True)
        return redirect('notification_list')

    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    }
    return render(request, 'accounts/notification_list.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """标记单个通知为已读"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()

        # 处理AJAX请求
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

            # 如果通知有相关链接，重定向到该链接
        if notification.link:
            return redirect(notification.link)

            # 否则返回通知列表
        return redirect('notification_list')
    except Notification.DoesNotExist:
        messages.error(request, '通知不存在')
        return redirect('notification_list')


@login_required
def get_unread_notifications(request):
    """获取未读通知 (用于AJAX请求)"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')[:5]  # 最新的5条未读通知

        notifications_data = []
        for notification in unread_notifications:
            notifications_data.append({
                'id': notification.id,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
                'link': notification.link
            })

        return JsonResponse({
            'status': 'success',
            'unread_count': unread_notifications.count(),
            'notifications': notifications_data
        })

    return JsonResponse({'status': 'error', 'message': '无效请求'})