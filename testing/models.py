# testing/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUser(models.Model):
    """测试用户模型"""

    TEST_ROLES = (
        ('AUTHOR', '测试作者'),
        ('REVIEWER', '测试审稿人'),
        ('EDITOR', '测试编辑'),
        ('ADMIN', '测试管理员'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='test_profile')
    test_role = models.CharField(max_length=20, choices=TEST_ROLES, verbose_name='测试角色')
    is_test_account = models.BooleanField(default=True, verbose_name='是否是测试账户')
    test_scenario = models.CharField(max_length=50, blank=True, null=True, verbose_name='测试场景')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')

    class Meta:
        verbose_name = '测试用户'
        verbose_name_plural = '测试用户'

    def __str__(self):
        return f"{self.user.username} - {self.get_test_role_display()}"

    @property
    def is_expired(self):
        """检查测试账户是否已过期"""
        from django.utils import timezone
        return timezone.now() > self.expires_at


# testing/models.py (继续添加)
class TestScenario(models.Model):
    """测试场景模型"""

    name = models.CharField(max_length=100, verbose_name='场景名称')
    description = models.TextField(verbose_name='场景描述')
    applicable_roles = models.CharField(max_length=50, verbose_name='适用角色')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TestStep(models.Model):
    """测试步骤模型"""

    scenario = models.ForeignKey(TestScenario, on_delete=models.CASCADE, related_name='steps')
    step_number = models.PositiveIntegerField(verbose_name='步骤序号')
    title = models.CharField(max_length=100, verbose_name='步骤标题')
    description = models.TextField(verbose_name='步骤描述')
    expected_result = models.TextField(verbose_name='预期结果')
    url_path = models.CharField(max_length=200, blank=True, null=True, verbose_name='URL路径')

    class Meta:
        ordering = ['scenario', 'step_number']

    def __str__(self):
        return f"{self.scenario.name} - 步骤 {self.step_number}: {self.title}"


class TestSession(models.Model):
    """测试会话模型"""

    STATUS_CHOICES = (
        ('ACTIVE', '进行中'),
        ('COMPLETED', '已完成'),
        ('ABANDONED', '已放弃'),
    )

    test_user = models.ForeignKey(TestUser, on_delete=models.CASCADE, related_name='test_sessions')
    scenario = models.ForeignKey(TestScenario, on_delete=models.CASCADE, related_name='test_sessions')
    current_step = models.PositiveIntegerField(default=1, verbose_name='当前步骤')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.test_user} - {self.scenario.name}"


# testing/models.py (继续添加)
class TestFeedback(models.Model):
    """测试反馈模型"""

    SATISFACTION_CHOICES = (
        (1, '非常不满意'),
        (2, '不满意'),
        (3, '一般'),
        (4, '满意'),
        (5, '非常满意')
    )

    test_session = models.OneToOneField(TestSession, on_delete=models.CASCADE, related_name='feedback')
    satisfaction_rating = models.IntegerField(choices=SATISFACTION_CHOICES, verbose_name='满意度评分')
    ui_rating = models.IntegerField(choices=SATISFACTION_CHOICES, verbose_name='界面评分')
    usability_rating = models.IntegerField(choices=SATISFACTION_CHOICES, verbose_name='易用性评分')
    performance_rating = models.IntegerField(choices=SATISFACTION_CHOICES, verbose_name='性能评分')
    comments = models.TextField(blank=True, verbose_name='反馈意见')
    encountered_issues = models.TextField(blank=True, verbose_name='遇到的问题')
    suggestions = models.TextField(blank=True, verbose_name='改进建议')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"反馈 - {self.test_session}"

    @property
    def average_rating(self):
        """计算平均评分"""
        ratings = [
            self.satisfaction_rating,
            self.ui_rating,
            self.usability_rating,
            self.performance_rating
        ]
        return sum(ratings) / len(ratings)