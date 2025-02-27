# accounts/models.py  
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLES = (
        ('AUTHOR', '作者'),
        ('REVIEWER', '审稿人'),
        ('EDITOR', '编辑'),
        ('ADMIN', '管理员'),
    )

    role = models.CharField(max_length=20, choices=ROLES, default='AUTHOR', verbose_name='角色')
    phone = models.CharField(max_length=20, blank=True, verbose_name='电话')
    institution = models.CharField(max_length=100, blank=True, verbose_name='所属机构')
    title = models.CharField(max_length=50, blank=True, verbose_name='职称')
    address = models.CharField(max_length=200, blank=True, verbose_name='通讯地址')
    bio = models.TextField(blank=True, verbose_name='个人简介')
    research_field = models.CharField(max_length=100, blank=True, verbose_name='研究领域')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # accounts/models.py (添加以下代码)


class Notification(models.Model):
    """用户通知模型"""
    NOTIFICATION_TYPES = (
        ('INFO', '信息'),
        ('SUCCESS', '成功'),
        ('WARNING', '警告'),
        ('ERROR', '错误'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='用户')
    message = models.TextField(verbose_name='通知内容')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='INFO',
                                         verbose_name='通知类型')
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name='相关链接')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知列表'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.message[:30]}"