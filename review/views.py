# review/views.py  
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from accounts.utils import create_notification
from submission.models import Paper
from accounts.models import User
from .models import Review, EditorDecision
from .forms import ReviewForm, ReviewInvitationResponseForm, AssignReviewersForm, EditorDecisionForm, DateRangeForm


@login_required
def reviewer_dashboard(request):
    """审稿人仪表板"""
    # 检查用户是否是审稿人  
    if request.user.role != 'REVIEWER' and not request.user.is_staff:
        messages.error(request, '只有审稿人才能访问审稿仪表板。')
        return redirect('home')

        # 获取分配给当前用户的审稿任务
    pending_reviews = Review.objects.filter(
        reviewer=request.user,
        is_completed=False,
        accepted_at__isnull=False
    ).select_related('paper')

    # 获取邀请但尚未回应的审稿任务  
    invited_reviews = Review.objects.filter(
        reviewer=request.user,
        is_completed=False,
        accepted_at__isnull=True
    ).select_related('paper')

    # 获取已完成的审稿任务  
    completed_reviews = Review.objects.filter(
        reviewer=request.user,
        is_completed=True
    ).select_related('paper').order_by('-submitted_at')

    return render(request, 'review/reviewer_dashboard.html', {
        'pending_reviews': pending_reviews,
        'invited_reviews': invited_reviews,
        'completed_reviews': completed_reviews
    })


@login_required
def review_invitation_response(request, review_id):
    """回应审稿邀请"""
    review = get_object_or_404(Review, id=review_id)

    # 检查权限  
    if request.user != review.reviewer:
        messages.error(request, '您没有权限回应此审稿邀请。')
        return redirect('reviewer_dashboard')

    if review.accepted_at is not None:
        messages.error(request, '您已经回应过此审稿邀请。')
        return redirect('reviewer_dashboard')

    if request.method == 'POST':
        form = ReviewInvitationResponseForm(request.POST)
        if form.is_valid():
            response = form.cleaned_data['response']

            if response == 'ACCEPT':
                review.accepted_at = timezone.now()
                review.save()
                messages.success(request, '感谢您接受审稿邀请！请在截止日期前完成审稿。')
            else:
                # 拒绝邀请，删除审稿记录  
                reason = form.cleaned_data['reason']
                # 这里可以添加发送邮件通知编辑的代码  
                review.delete()
                messages.info(request, '您已婉拒审稿邀请，感谢您的回复。')

            return redirect('reviewer_dashboard')
    else:
        form = ReviewInvitationResponseForm()

    return render(request, 'review/invitation_response.html', {
        'form': form,
        'review': review,
        'paper': review.paper
    })


@login_required
def review_paper(request, review_id):
    """审稿页面"""
    review = get_object_or_404(Review, id=review_id)

    # 检查权限  
    if request.user != review.reviewer:
        messages.error(request, '您没有权限审阅此稿件。')
        return redirect('reviewer_dashboard')

    if review.accepted_at is None:
        messages.error(request, '请先接受审稿邀请。')
        return redirect('review_invitation_response', review_id=review.id)

    if review.is_completed:
        messages.info(request, '您已经完成了此稿件的审阅。')
        return redirect('reviewer_dashboard')

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_completed = True
            review.submitted_at = timezone.now()
            review.save()

            # 检查是否所有审稿人都已提交评审  
            paper = review.paper
            total_reviews = paper.reviews.count()
            completed_reviews = paper.reviews.filter(is_completed=True).count()

            if total_reviews == completed_reviews:
                # 所有审稿人都已提交评审，更新论文状态  
                paper.status = 'REVIEW_COMPLETED'
                paper.save()

            messages.success(request, '审稿意见提交成功！感谢您的贡献。')
            return redirect('reviewer_dashboard')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'review/review_paper.html', {
        'form': form,
        'review': review,
        'paper': review.paper
    })


@login_required
def editor_dashboard(request):
    """编辑仪表板"""
    # 检查用户是否是编辑  
    if request.user.role != 'EDITOR' and not request.user.is_staff:
        messages.error(request, '只有编辑才能访问编辑仪表板。')
        return redirect('home')

        # 获取新提交的稿件
    new_submissions = Paper.objects.filter(status='SUBMITTED').order_by('-submitted_at')

    # 获取审稿中的稿件  
    under_review = Paper.objects.filter(status__in=['INITIAL_CHECK', 'UNDER_REVIEW', 'REVIEW_COMPLETED']).order_by(
        '-last_updated')

    # 获取需要编辑决定的稿件  
    need_decision = Paper.objects.filter(status='REVIEW_COMPLETED').order_by('-last_updated')

    # 获取已决定的稿件  
    decided = Paper.objects.filter(status__in=['ACCEPTED', 'REJECTED', 'REVISION_REQUIRED']).order_by('-last_updated')

    return render(request, 'review/editor_dashboard.html', {
        'new_submissions': new_submissions,
        'under_review': under_review,
        'need_decision': need_decision,
        'decided': decided
    })


@login_required
def assign_reviewers(request, paper_id):
    """分配审稿人"""
    paper = get_object_or_404(Paper, id=paper_id)

    # 检查权限  
    if request.user.role != 'EDITOR' and not request.user.is_staff:
        messages.error(request, '只有编辑才能分配审稿人。')
        return redirect('home')

        # 获取当前已分配的审稿人
    current_reviewers = paper.reviews.values_list('reviewer', flat=True)

    # 获取可选的审稿人（角色为审稿人且不是论文作者的用户）  
    available_reviewers = User.objects.filter(
        Q(role='REVIEWER') | Q(is_staff=True)
    ).exclude(
        id=paper.author.id
    ).exclude(
        id__in=current_reviewers
    ).order_by('last_name', 'first_name')

    if request.method == 'POST':
        form = AssignReviewersForm(request.POST, reviewers_queryset=available_reviewers)
        if form.is_valid():
            selected_reviewers = form.cleaned_data['reviewers']

            # 为每个选定的审稿人创建审稿记录  
            for reviewer in selected_reviewers:
                Review.objects.create(
                    paper=paper,
                    reviewer=reviewer
                )

                # 更新论文状态
            if paper.status == 'SUBMITTED':
                paper.status = 'INITIAL_CHECK'
                paper.save()

            messages.success(request, f'成功分配了 {len(selected_reviewers)} 位审稿人。')
            return redirect('submission_detail', paper_id=paper.id)
    else:
        form = AssignReviewersForm(reviewers_queryset=available_reviewers)

        # 获取已分配的审稿人信息
    assigned_reviewers = Review.objects.filter(paper=paper).select_related('reviewer')

    if form.is_valid():
        # 保存审稿分配...

        # 为每个审稿人创建通知
        for reviewer in form.cleaned_data['reviewers']:
            create_notification(
                user=reviewer,
                message=f'您收到一个新的审稿邀请：《{paper.title}》，请尽快处理。',
                notification_type='INFO',
                link=reverse('review_detail', args=[review.id])
            )

        messages.success(request, '审稿人分配成功！')
        return redirect('submission_detail', paper_id)

    return render(request, 'review/assign_reviewers.html', {
        'form': form,
        'paper': paper,
        'assigned_reviewers': assigned_reviewers
    })


@login_required
def editor_decision(request, paper_id):
    """编辑决定"""
    paper = get_object_or_404(Paper, id=paper_id)

    # 检查权限  
    if request.user.role != 'EDITOR' and not request.user.is_staff:
        messages.error(request, '只有编辑才能做出决定。')
        return redirect('home')

        # 检查是否有足够的审稿意见
    reviews = paper.reviews.filter(is_completed=True)
    if not reviews.exists():
        messages.error(request, '尚无审稿意见，无法做出决定。')
        return redirect('submission_detail', paper_id=paper.id)

    if request.method == 'POST':
        form = EditorDecisionForm(request.POST)
        if form.is_valid():
            decision = form.save(commit=False)
            decision.paper = paper
            decision.editor = request.user
            decision.save()

            # 更新论文状态  
            if decision.decision == 'ACCEPT':
                paper.status = 'ACCEPTED'
            elif decision.decision == 'REJECT':
                paper.status = 'REJECTED'
            else:  # MINOR_REVISION 或 MAJOR_REVISION  
                paper.status = 'REVISION_REQUIRED'

            paper.last_updated = timezone.now()
            paper.save()

            messages.success(request, '编辑决定已保存。')
            return redirect('submission_detail', paper_id=paper.id)
    else:
        form = EditorDecisionForm()

    return render(request, 'review/editor_decision.html', {
        'form': form,
        'paper': paper,
        'reviews': reviews
    })


# review/views.py (添加以下代码)
from django.db.models import Count, Avg, F, Q, DurationField, ExpressionWrapper, FloatField
from django.db.models.functions import TruncMonth, TruncYear, Cast
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
import json


@login_required
def statistics_dashboard(request):
    """统计仪表板视图"""
    # 权限检查
    if request.user.role != 'EDITOR' and not request.user.is_staff:
        messages.error(request, '只有编辑才能查看统计数据。')
        return redirect('home')

        # 获取统计时间范围
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)  # 默认显示一年的数据

    date_range_form = DateRangeForm(request.GET or None)
    if date_range_form.is_valid():
        start_date = date_range_form.cleaned_data['start_date']
        end_date = date_range_form.cleaned_data['end_date']

        # 基础统计数据
    total_submissions = Paper.objects.filter(submitted_at__date__range=[start_date, end_date]).count()
    accepted_papers = Paper.objects.filter(status='ACCEPTED', last_updated__date__range=[start_date, end_date]).count()
    rejected_papers = Paper.objects.filter(status='REJECTED', last_updated__date__range=[start_date, end_date]).count()
    under_review_papers = Paper.objects.filter(status__in=['INITIAL_CHECK', 'UNDER_REVIEW']).count()

    # 计算接受率和拒绝率
    decision_count = accepted_papers + rejected_papers
    acceptance_rate = (accepted_papers / decision_count * 100) if decision_count > 0 else 0
    rejection_rate = (rejected_papers / decision_count * 100) if decision_count > 0 else 0

    # 按月份统计稿件
    submissions_by_month = Paper.objects.filter(
        submitted_at__date__range=[start_date, end_date]
    ).annotate(
        month=TruncMonth('submitted_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # 将查询结果转换为前端需要的格式
    months_labels = []
    submissions_data = []
    for item in submissions_by_month:
        months_labels.append(item['month'].strftime('%Y-%m'))
        submissions_data.append(item['count'])

        # 按栏目统计稿件
    submissions_by_category = Paper.objects.filter(
        submitted_at__date__range=[start_date, end_date]
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')

    category_labels = [item['category__name'] for item in submissions_by_category]
    category_data = [item['count'] for item in submissions_by_category]

    # 审稿周期统计
    review_duration = Review.objects.filter(
        is_completed=True,
        submitted_at__date__range=[start_date, end_date]
    ).annotate(
        duration=ExpressionWrapper(
            F('submitted_at') - F('accepted_at'),
            output_field=DurationField()
        )
    ).aggregate(
        avg_days=Avg(Cast('duration', output_field=FloatField()) / (24 * 3600 * 1000000))
    )

    avg_review_days = round(review_duration['avg_days'] or 0, 1)

    # 审稿人工作量排名
    top_reviewers = Review.objects.filter(
        is_completed=True,
        submitted_at__date__range=[start_date, end_date]
    ).values('reviewer__username', 'reviewer__first_name', 'reviewer__last_name').annotate(
        completed_reviews=Count('id')
    ).order_by('-completed_reviews')[:10]

    # 稿件状态分布
    status_distribution = Paper.objects.filter(
        submitted_at__date__range=[start_date, end_date]
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')

    status_labels = [item['status'] for item in status_distribution]
    status_data = [item['count'] for item in status_distribution]

    # 渲染模板
    context = {
        'form': date_range_form,
        'start_date': start_date,
        'end_date': end_date,
        'total_submissions': total_submissions,
        'accepted_papers': accepted_papers,
        'rejected_papers': rejected_papers,
        'under_review_papers': under_review_papers,
        'acceptance_rate': round(acceptance_rate, 1),
        'rejection_rate': round(rejection_rate, 1),
        'avg_review_days': avg_review_days,
        'top_reviewers': top_reviewers,
        'months_labels': json.dumps(months_labels),
        'submissions_data': json.dumps(submissions_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
    }

    return render(request, 'review/statistics_dashboard.html', context)


@login_required
def export_submissions_csv(request):
    """导出稿件数据为CSV格式"""
    # 权限检查
    if request.user.role != 'EDITOR' and not request.user.is_staff:
        messages.error(request, '只有编辑才能导出数据。')
        return redirect('home')

        # 获取时间范围
    date_range_form = DateRangeForm(request.GET or None)
    if date_range_form.is_valid():
        start_date = date_range_form.cleaned_data['start_date']
        end_date = date_range_form.cleaned_data['end_date']
    else:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)

        # 查询稿件数据
    papers = Paper.objects.filter(
        submitted_at__date__range=[start_date, end_date]
    ).select_related('author', 'category').order_by('-submitted_at')

    # 创建CSV响应
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="submissions_{start_date}_to_{end_date}.csv"'

    # 创建CSV写入器
    writer = csv.writer(response)
    writer.writerow([
        '稿件ID', '标题', '作者', '栏目', '状态', '提交时间', '最后更新时间', '审稿人数量'
    ])

    # 写入数据
    for paper in papers:
        writer.writerow([
            paper.id,
            paper.title,
            paper.author.get_full_name(),
            paper.category.name,
            paper.get_status_display(),
            paper.submitted_at.strftime('%Y-%m-%d'),
            paper.last_updated.strftime('%Y-%m-%d'),
            paper.reviews.count()
        ])

    return response


@login_required
def export_reviews_csv(request):
    """导出审稿数据为CSV格式"""
    # 权限检查
    if request.user.role != 'EDITOR' and not request.user.is_staff:
        messages.error(request, '只有编辑才能导出数据。')
        return redirect('home')

        # 获取时间范围
    date_range_form = DateRangeForm(request.GET or None)
    if date_range_form.is_valid():
        start_date = date_range_form.cleaned_data['start_date']
        end_date = date_range_form.cleaned_data['end_date']
    else:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)

        # 查询审稿数据
    reviews = Review.objects.filter(
        is_completed=True,
        submitted_at__date__range=[start_date, end_date]
    ).select_related('paper', 'reviewer').order_by('-submitted_at')

    # 创建CSV响应
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reviews_{start_date}_to_{end_date}.csv"'

    # 创建CSV写入器
    writer = csv.writer(response)
    writer.writerow([
        '审稿ID', '稿件标题', '审稿人', '推荐决定', '创新性评分', '方法学评分',
        '文献评分', '写作评分', '审稿开始时间', '审稿完成时间', '审稿天数'
    ])

    # 写入数据
    for review in reviews:
        # 计算审稿天数
        if review.accepted_at and review.submitted_at:
            review_days = (review.submitted_at - review.accepted_at).days
        else:
            review_days = None

        writer.writerow([
            review.id,
            review.paper.title,
            review.reviewer.get_full_name(),
            review.get_recommendation_display(),
            review.score_originality,
            review.score_methodology,
            review.score_literature,
            review.score_writing,
            review.accepted_at.strftime('%Y-%m-%d') if review.accepted_at else 'N/A',
            review.submitted_at.strftime('%Y-%m-%d') if review.submitted_at else 'N/A',
            review_days
        ])

    return response


# review/views.py (添加以下视图)
@login_required
def review_duration_analysis(request):
    """审稿周期详细分析"""
    # 权限检查
    if request.user.role != 'EDITOR' and not request.user.is_staff:
        messages.error(request, '只有编辑才能查看统计数据。')
        return redirect('home')

        # 获取统计时间范围
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)  # 默认显示一年的数据

    date_range_form = DateRangeForm(request.GET or None)
    if date_range_form.is_valid():
        start_date = date_range_form.cleaned_data['start_date']
        end_date = date_range_form.cleaned_data['end_date']

        # 查询完成的审稿记录
    completed_reviews = Review.objects.filter(
        is_completed=True,
        submitted_at__date__range=[start_date, end_date]
    ).select_related('paper', 'reviewer')

    # 计算审稿周期
    review_durations = []
    for review in completed_reviews:
        if review.accepted_at and review.submitted_at:
            duration = (review.submitted_at - review.accepted_at).days
            review_durations.append({
                'review_id': review.id,
                'paper_title': review.paper.title,
                'reviewer_name': review.reviewer.get_full_name(),
                'accepted_at': review.accepted_at,
                'submitted_at': review.submitted_at,
                'duration_days': duration
            })

            # 计算平均值、中位数、最长和最短周期
    if review_durations:
        durations = [d['duration_days'] for d in review_durations]
        avg_duration = sum(durations) / len(durations)
        median_duration = sorted(durations)[len(durations) // 2]
        max_duration = max(durations)
        min_duration = min(durations)
    else:
        avg_duration = median_duration = max_duration = min_duration = 0

        # 按时长分类
    duration_ranges = {
        '1周内': 0,
        '1-2周': 0,
        '2-3周': 0,
        '3-4周': 0,
        '1-2月': 0,
        '2月以上': 0
    }

    for d in review_durations:
        days = d['duration_days']
        if days <= 7:
            duration_ranges['1周内'] += 1
        elif days <= 14:
            duration_ranges['1-2周'] += 1
        elif days <= 21:
            duration_ranges['2-3周'] += 1
        elif days <= 28:
            duration_ranges['3-4周'] += 1
        elif days <= 60:
            duration_ranges['1-2月'] += 1
        else:
            duration_ranges['2月以上'] += 1

            # 准备图表数据
    duration_labels = list(duration_ranges.keys())
    duration_data = list(duration_ranges.values())

    context = {
        'form': date_range_form,
        'start_date': start_date,
        'end_date': end_date,
        'review_durations': sorted(review_durations, key=lambda x: x['duration_days'], reverse=True),
        'avg_duration': round(avg_duration, 1),
        'median_duration': median_duration,
        'max_duration': max_duration,
        'min_duration': min_duration,
        'total_reviews': len(review_durations),
        'duration_labels': json.dumps(duration_labels),
        'duration_data': json.dumps(duration_data),
    }

    return render(request, 'review/review_duration_analysis.html', context)