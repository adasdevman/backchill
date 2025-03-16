from rest_framework import serializers
from core.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'created']
        read_only_fields = ['created'] 