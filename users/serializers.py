from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 
            'email', 
            'first_name', 
            'last_name', 
            'role', 
            'profile_image',
            'phone_number',
            'address',
            'city',
            'username'
        )

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'address',
            'city',
            'role',
            'profile_image'
        )
        read_only_fields = ('email', 'role') 