from django.db import models
from users.models import User
from .base import TimeStampedModel

class Notification(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    @classmethod
    def send_to_users(cls, users, title, message):
        notifications = [
            cls(user=user, title=title, message=message)
            for user in users
        ]
        return cls.objects.bulk_create(notifications)

    @classmethod
    def send_to_role(cls, role, title, message):
        users = User.objects.filter(role=role)
        return cls.send_to_users(users, title, message)

    @classmethod
    def send_to_all(cls, title, message):
        users = User.objects.all()
        return cls.send_to_users(users, title, message)