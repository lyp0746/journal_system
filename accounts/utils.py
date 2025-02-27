# accounts/utils.py
from .models import Notification

def create_notification(user, message, notification_type='INFO', link=None):
    """创建用户通知的辅助函数"""
    notification = Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        link=link
    )
    return notification