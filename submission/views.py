# submission/views.py  
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from accounts.utils import create_notification
from .models import Paper, Revision, Category
from .forms import PaperSubmissionForm, RevisionForm
from django.core.paginator import Paginator


@login_required
def paper_submission(request):
    """论文投稿视图"""
    if request.method == 'POST':
        form = PaperSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.author = request.user
            paper.status = 'SUBMITTED'
            paper.submitted_at = timezone.now()
            paper.save()

            messages.success(request, '论文投稿成功！您的稿件已提交，我们将尽快处理。')
            return redirect('submission_list')
    else:
        form = PaperSubmissionForm()
    if form.is_valid():
        # 保存稿件...

        # 创建通知
        create_notification(
            user=request.user,
            message=f'您的稿件《{paper.title}》已成功提交，感谢您的投稿！',
            notification_type='SUCCESS',
            link=reverse('submission_detail', args=[paper.id])
        )

        messages.success(request, f'稿件《{paper.title}》提交成功！')
        return redirect('submission_detail', paper.id)

    return render(request, 'submission/submit_paper.html', {'form': form})


@login_required
def submission_list(request):
    """作者的论文投稿列表"""
    # 获取当前用户的所有论文  
    papers = Paper.objects.filter(author=request.user).order_by('-submitted_at')

    # 添加分页  
    paginator = Paginator(papers, 10)  # 每页显示10篇论文  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'submission/submission_list.html', {'page_obj': page_obj})


@login_required
def submission_detail(request, paper_id):
    """论文详情视图"""
    paper = get_object_or_404(Paper, id=paper_id)

    # 检查权限：只有作者或编辑可以查看  
    if request.user != paper.author and not request.user.role == 'EDITOR' and not request.user.is_staff:
        messages.error(request, '您没有权限查看此稿件。')
        return redirect('submission_list')

        # 获取论文的所有修改版本
    revisions = paper.revisions.all().order_by('version')

    # 获取论文的所有审稿意见  
    reviews = paper.reviews.all()

    return render(request, 'submission/submission_detail.html', {
        'paper': paper,
        'revisions': revisions,
        'reviews': reviews
    })


@login_required
def paper_revision(request, paper_id):
    """论文修改视图"""
    paper = get_object_or_404(Paper, id=paper_id)

    # 检查权限：只有作者可以修改，且论文状态必须是需要修改  
    if request.user != paper.author:
        messages.error(request, '您没有权限修改此稿件。')
        return redirect('submission_list')

    if paper.status != 'REVISION_REQUIRED':
        messages.error(request, '此稿件当前不需要修改。')
        return redirect('submission_detail', paper_id=paper.id)

    if request.method == 'POST':
        form = RevisionForm(request.POST, request.FILES)
        if form.is_valid():
            revision = form.save(commit=False)
            revision.paper = paper

            # 获取当前最高版本号  
            last_version = paper.revisions.order_by('-version').first()
            if last_version:
                revision.version = last_version.version + 1
            else:
                revision.version = 1

            revision.save()

            # 更新论文状态  
            paper.status = 'UNDER_REVIEW'
            paper.last_updated = timezone.now()
            paper.save()

            messages.success(request, '论文修改稿提交成功！')
            return redirect('submission_detail', paper_id=paper.id)
    else:
        form = RevisionForm()

    return render(request, 'submission/paper_revision.html', {'form': form, 'paper': paper})


@login_required
def withdraw_submission(request, paper_id):
    """撤回投稿"""
    paper = get_object_or_404(Paper, id=paper_id)

    # 检查权限：只有作者可以撤回，且论文状态不能是已拒绝或已接受  
    if request.user != paper.author:
        messages.error(request, '您没有权限撤回此稿件。')
        return redirect('submission_list')

    if paper.status in ['REJECTED', 'ACCEPTED', 'PUBLISHED']:
        messages.error(request, f'稿件状态为"{paper.get_status_display()}"，不能撤回。')
        return redirect('submission_detail', paper_id=paper.id)

    if request.method == 'POST':
        paper.status = 'DRAFT'
        paper.save()
        messages.success(request, '稿件已成功撤回。')
        return redirect('submission_list')

    return render(request, 'submission/withdraw_confirmation.html', {'paper': paper})

