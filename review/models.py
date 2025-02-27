# review/models.py  
from django.db import models
from django.conf import settings
from submission.models import Paper


class Review(models.Model):
    """审稿模型"""
    RECOMMENDATION_CHOICES = (
        ('ACCEPT', '接受'),
        ('MINOR_REVISION', '小修改后接受'),
        ('MAJOR_REVISION', '大修改后重审'),
        ('REJECT', '拒绝'),
    )

    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    # 评审结果
    recommendation = models.CharField(max_length=20, choices=RECOMMENDATION_CHOICES, null=True, blank=True)
    comments_to_author = models.TextField(null=True, blank=True)
    comments_to_editor = models.TextField(null=True, blank=True)

    # 评分 (1-5分)
    score_originality = models.PositiveSmallIntegerField(null=True, blank=True)
    score_methodology = models.PositiveSmallIntegerField(null=True, blank=True)
    score_literature = models.PositiveSmallIntegerField(null=True, blank=True)
    score_writing = models.PositiveSmallIntegerField(null=True, blank=True)

    # 审稿附件
    review_file = models.FileField(upload_to='reviews/', null=True, blank=True)

    class Meta:
        unique_together = ('paper', 'reviewer')

    def __str__(self):
        return f"Review of {self.paper.title} by {self.reviewer.username}"


class EditorDecision(models.Model):
    """编辑决定模型"""
    DECISION_CHOICES = (
        ('ACCEPT', '接受'),
        ('MINOR_REVISION', '小修改后接受'),
        ('MAJOR_REVISION', '大修改后重审'),
        ('REJECT', '拒绝'),
    )

    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='decisions')
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='decisions')
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Decision on {self.paper.title}: {self.get_decision_display()}"