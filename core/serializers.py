from rest_framework import serializers
from .models import BillingInfo

class BillingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingInfo
        fields = ['id', 'user', 'first_name', 'last_name', 'email', 'phone', 
                 'address', 'city', 'updated_at']
        read_only_fields = ['user', 'updated_at'] 