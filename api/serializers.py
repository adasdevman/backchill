from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from users.models import User
import uuid
from core.models.payment import Payment
from core.serializers.payment import PaymentSerializer as CorePaymentSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'role')
        read_only_fields = ('id',)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        user = authenticate(
            email=data.get('email', ''),
            password=data.get('password', '')
        )
        if not user:
            raise serializers.ValidationError(_("Invalid credentials"))
        data['user'] = user
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'profile_image', 'banner_image')

class AnnonceurRegisterSerializer(RegisterSerializer):
    class Meta(RegisterSerializer.Meta):
        fields = RegisterSerializer.Meta.fields + ('role',)

    def create(self, validated_data):
        validated_data['role'] = 'ANNONCEUR'
        return super().create(validated_data)

# Use the core PaymentSerializer instead of redefining it here
PaymentSerializer = CorePaymentSerializer 