# testing/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from .models import TestUser
from .forms import TestUserForm

User = get_user_model()


def is_admin(user):
    """检查用户是否是管理员"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def manage_test_accounts(request):
    """管理测试账户"""
    test_users = TestUser.objects.all().order_by('-created_at')

    context = {
        'test_users': test_users,
    }
    return render(request, 'testing/manage_test_accounts.html', context)


@login_required
@user_passes_test(is_admin)
def create_test_account(request):
    """创建测试账户"""
    if request.method == 'POST':
        form = TestUserForm(request.POST)
        if form.is_valid():
            # 创建用户
            username = f"test_{form.cleaned_data['test_role'].lower()}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
            password = User.objects.make_random_password()
            email = f"{username}@test.example.com"

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # 设置用户角色
            user.role = form.cleaned_data['test_role']
            user.save()

            # 创建测试用户资料
            expires_at = timezone.now() + timedelta(days=form.cleaned_data['expiry_days'])
            test_user = TestUser.objects.create(
                user=user,
                test_role=form.cleaned_data['test_role'],
                test_scenario=form.cleaned_data['test_scenario'],
                expires_at=expires_at
            )

            messages.success(request, f'测试账户创建成功! 用户名: {username}, 密码: {password}')
            return redirect('view_test_account', test_user.id)
    else:
        form = TestUserForm()

    context = {
        'form': form,
    }
    return render(request, 'testing/create_test_account.html', context)


@login_required
@user_passes_test(is_admin)
def view_test_account(request, test_user_id):
    """查看测试账户详情"""
    test_user = get_object_or_404(TestUser, id=test_user_id)

    context = {
        'test_user': test_user,
    }
    return render(request, 'testing/view_test_account.html', context)


@login_required
@user_passes_test(is_admin)
def delete_test_account(request, test_user_id):
    """删除测试账户"""
    test_user = get_object_or_404(TestUser, id=test_user_id)

    if request.method == 'POST':
        user = test_user.user
        test_user.delete()
        user.delete()
        messages.success(request, '测试账户已成功删除')
        return redirect('manage_test_accounts')

    context = {
        'test_user': test_user,
    }
    return render(request, 'testing/delete_test_account.html', context)


@login_required
@user_passes_test(is_admin)
def extend_test_account(request, test_user_id):
    """延长测试账户有效期"""
    test_user = get_object_or_404(TestUser, id=test_user_id)

    if request.method == 'POST':
        days = int(request.POST.get('days', 7))
        test_user.expires_at = test_user.expires_at + timedelta(days=days)
        test_user.save()
        messages.success(request, f'测试账户有效期已延长 {days} 天')
        return redirect('view_test_account', test_user.id)

    context = {
        'test_user': test_user,
    }
    return render(request, 'testing/extend_test_account.html', context)


# testing/views.py (继续添加)
from .models import TestScenario, TestStep, TestSession


@login_required
def test_dashboard(request):
    """测试仪表板"""
    # 检查是否是测试用户
    try:
        test_user = request.user.test_profile
    except:
        messages.error(request, '只有测试账户可以访问测试功能')
        return redirect('home')

        # 获取适用于当前角色的测试场景
    scenarios = TestScenario.objects.filter(applicable_roles__contains=test_user.test_role)

    # 获取用户的测试会话
    active_sessions = TestSession.objects.filter(
        test_user=test_user,
        status='ACTIVE'
    )

    completed_sessions = TestSession.objects.filter(
        test_user=test_user,
        status='COMPLETED'
    )

    context = {
        'test_user': test_user,
        'scenarios': scenarios,
        'active_sessions': active_sessions,
        'completed_sessions': completed_sessions,
    }
    return render(request, 'testing/test_dashboard.html', context)


@login_required
def start_test_scenario(request, scenario_id):
    """开始测试场景"""
    # 检查是否是测试用户
    try:
        test_user = request.user.test_profile
    except:
        messages.error(request, '只有测试账户可以访问测试功能')
        return redirect('home')

    scenario = get_object_or_404(TestScenario, id=scenario_id)

    # 创建新的测试会话
    session = TestSession.objects.create(
        test_user=test_user,
        scenario=scenario,
        current_step=1
    )

    return redirect('test_step', session_id=session.id, step_number=1)


@login_required
def test_step(request, session_id, step_number):
    """测试步骤"""
    # 检查是否是测试用户
    try:
        test_user = request.user.test_profile
    except:
        messages.error(request, '只有测试账户可以访问测试功能')
        return redirect('home')

    session = get_object_or_404(TestSession, id=session_id, test_user=test_user)

    if session.status != 'ACTIVE':
        messages.error(request, '该测试会话已结束')
        return redirect('test_dashboard')

        # 获取当前步骤
    try:
        step = TestStep.objects.get(scenario=session.scenario, step_number=step_number)
    except TestStep.DoesNotExist:
        messages.error(request, '测试步骤不存在')
        return redirect('test_dashboard')

        # 更新会话的当前步骤
    session.current_step = step_number
    session.save()

    # 获取场景的所有步骤
    all_steps = TestStep.objects.filter(scenario=session.scenario).order_by('step_number')
    total_steps = all_steps.count()

    # 计算进度
    progress = (step_number / total_steps) * 100

    # 判断是否是最后一步
    is_last_step = (step_number == total_steps)

    context = {
        'session': session,
        'step': step,
        'step_number': step_number,
        'total_steps': total_steps,
        'progress': progress,
        'is_last_step': is_last_step,
        'next_step': step_number + 1 if not is_last_step else None,
        'prev_step': step_number - 1 if step_number > 1 else None,
    }
    return render(request, 'testing/test_step.html', context)


@login_required
def complete_test(request, session_id):
    """完成测试"""
    # 检查是否是测试用户
    try:
        test_user = request.user.test_profile
    except:
        messages.error(request, '只有测试账户可以访问测试功能')
        return redirect('home')

    session = get_object_or_404(TestSession, id=session_id, test_user=test_user)

    if request.method == 'POST':
        session.status = 'COMPLETED'
        session.completed_at = timezone.now()
        session.save()

        messages.success(request, '测试已完成，感谢您的测试！')

        # 重定向到反馈表单
        return redirect('submit_test_feedback', session_id=session.id)

    context = {
        'session': session,
    }
    return render(request, 'testing/complete_test.html', context)


# testing/views.py (继续添加)
from .models import TestFeedback
from .forms import TestFeedbackForm


@login_required
def submit_test_feedback(request, session_id):
    """提交测试反馈"""
    # 检查是否是测试用户
    try:
        test_user = request.user.test_profile
    except:
        messages.error(request, '只有测试账户可以访问测试功能')
        return redirect('home')

    session = get_object_or_404(TestSession, id=session_id, test_user=test_user)

    # 检查会话是否已完成
    if session.status != 'COMPLETED':
        messages.error(request, '请先完成测试再提交反馈')
        return redirect('test_step', session_id=session.id, step_number=session.current_step)

        # 检查是否已提交反馈
    if hasattr(session, 'feedback'):
        messages.info(request, '您已经提交过反馈')
        return redirect('test_dashboard')

    if request.method == 'POST':
        form = TestFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.test_session = session
            feedback.save()

            messages.success(request, '感谢您的反馈！您的意见对我们改进系统非常重要。')
            return redirect('test_dashboard')
    else:
        form = TestFeedbackForm()

    context = {
        'form': form,
        'session': session,
    }
    return render(request, 'testing/submit_feedback.html', context)


@login_required
@user_passes_test(is_admin)
def view_test_feedbacks(request):
    """查看测试反馈"""
    feedbacks = TestFeedback.objects.all().order_by('-created_at')

    # 计算平均评分
    total_satisfaction = 0
    total_ui = 0
    total_usability = 0
    total_performance = 0
    feedback_count = feedbacks.count()

    if feedback_count > 0:
        for feedback in feedbacks:
            total_satisfaction += feedback.satisfaction_rating
            total_ui += feedback.ui_rating
            total_usability += feedback.usability_rating
            total_performance += feedback.performance_rating

        avg_satisfaction = total_satisfaction / feedback_count
        avg_ui = total_ui / feedback_count
        avg_usability = total_usability / feedback_count
        avg_performance = total_performance / feedback_count
        avg_overall = (avg_satisfaction + avg_ui + avg_usability + avg_performance) / 4
    else:
        avg_satisfaction = avg_ui = avg_usability = avg_performance = avg_overall = 0

    context = {
        'feedbacks': feedbacks,
        'feedback_count': feedback_count,
        'avg_satisfaction': avg_satisfaction,
        'avg_ui': avg_ui,
        'avg_usability': avg_usability,
        'avg_performance': avg_performance,
        'avg_overall': avg_overall,
    }
    return render(request, 'testing/view_feedbacks.html', context)


# testing/views.py (继续添加)
import json
from django.http import JsonResponse
from django.db.models import Count, Avg


@login_required
@user_passes_test(is_admin)
def test_analytics_dashboard(request):
    """测试分析仪表板"""
    # 获取测试会话数据
    test_sessions = TestSession.objects.all()

    # 按场景统计测试会话数量
    sessions_by_scenario = TestSession.objects.values('scenario__name').annotate(
        count=Count('id')
    ).order_by('-count')

    # 按状态统计测试会话
    sessions_by_status = TestSession.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    # 按角色统计测试用户
    users_by_role = TestUser.objects.values('test_role').annotate(
        count=Count('id')
    ).order_by('test_role')

    # 获取反馈评分数据
    feedback_data = TestFeedback.objects.aggregate(
        avg_satisfaction=Avg('satisfaction_rating'),
        avg_ui=Avg('ui_rating'),
        avg_usability=Avg('usability_rating'),
        avg_performance=Avg('performance_rating'),
    )

    context = {
        'total_sessions': test_sessions.count(),
        'completed_sessions': test_sessions.filter(status='COMPLETED').count(),
        'active_sessions': test_sessions.filter(status='ACTIVE').count(),
        'total_users': TestUser.objects.count(),
        'total_feedbacks': TestFeedback.objects.count(),
        'sessions_by_scenario': sessions_by_scenario,
        'sessions_by_status': sessions_by_status,
        'users_by_role': users_by_role,
        'feedback_data': feedback_data,
    }
    return render(request, 'testing/analytics_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def test_analytics_chart_data(request):
    """获取测试分析图表数据"""
    chart_type = request.GET.get('type', 'sessions_by_date')

    if chart_type == 'sessions_by_date':
        # 按日期统计会话数量
        from django.db.models.functions import TruncDate

        sessions_by_date = TestSession.objects.annotate(
            date=TruncDate('started_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        dates = [item['date'].strftime('%Y-%m-%d') for item in sessions_by_date]
        counts = [item['count'] for item in sessions_by_date]

        return JsonResponse({
            'labels': dates,
            'datasets': [{
                'label': '测试会话数量',
                'data': counts,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        })

    elif chart_type == 'ratings_radar':
        # 获取评分雷达图数据
        feedback_data = TestFeedback.objects.aggregate(
            avg_satisfaction=Avg('satisfaction_rating'),
            avg_ui=Avg('ui_rating'),
            avg_usability=Avg('usability_rating'),
            avg_performance=Avg('performance_rating'),
        )

        return JsonResponse({
            'labels': ['满意度', '界面', '易用性', '性能'],
            'datasets': [{
                'label': '平均评分',
                'data': [
                    feedback_data['avg_satisfaction'] or 0,
                    feedback_data['avg_ui'] or 0,
                    feedback_data['avg_usability'] or 0,
                    feedback_data['avg_performance'] or 0,
                ],
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            }]
        })

    elif chart_type == 'users_by_role_pie':
        # 按角色统计用户
        users_by_role = TestUser.objects.values('test_role').annotate(
            count=Count('id')
        ).order_by('test_role')

        labels = []
        data = []

        for item in users_by_role:
            role_display = dict(TestUser.TEST_ROLES).get(item['test_role'], item['test_role'])
            labels.append(role_display)
            data.append(item['count'])

        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                ],
                'borderWidth': 1
            }]
        })

    return JsonResponse({'error': '未知图表类型'})


@login_required
@user_passes_test(is_admin)
def generate_test_report(request):
    """生成测试报告"""
    # 获取基本统计数据
    total_users = TestUser.objects.count()
    active_users = TestUser.objects.filter(expires_at__gt=timezone.now()).count()
    total_sessions = TestSession.objects.count()
    completed_sessions = TestSession.objects.filter(status='COMPLETED').count()
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0

    # 获取反馈统计
    feedback_count = TestFeedback.objects.count()
    feedback_stats = TestFeedback.objects.aggregate(
        avg_satisfaction=Avg('satisfaction_rating'),
        avg_ui=Avg('ui_rating'),
        avg_usability=Avg('usability_rating'),
        avg_performance=Avg('performance_rating'),
    )

    # 测试场景统计
    scenario_stats = TestScenario.objects.annotate(
        session_count=Count('test_sessions'),
        completion_count=Count('test_sessions', filter=models.Q(test_sessions__status='COMPLETED')),
    ).values('name', 'session_count', 'completion_count')

    # 获取最新反馈
    recent_feedbacks = TestFeedback.objects.order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'completion_rate': completion_rate,
        'feedback_count': feedback_count,
        'feedback_stats': feedback_stats,
        'scenario_stats': scenario_stats,
        'recent_feedbacks': recent_feedbacks,
        'generation_time': timezone.now(),
    }
    return render(request, 'testing/test_report.html', context)