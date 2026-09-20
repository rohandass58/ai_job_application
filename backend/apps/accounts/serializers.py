# apps/accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from core.models import EmailCredential
from core.crypto import encrypt

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2", "first_name", "last_name")
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class EmailCredentialSerializer(serializers.ModelSerializer):
    """Serializer for user's SMTP credentials (Gmail App Password)"""
    password = serializers.CharField(write_only=True, required=True, help_text="Gmail App Password (16 characters)")
    
    class Meta:
        model = EmailCredential
        fields = ("id", "email", "smtp_host", "smtp_port", "password", "is_verified")
        read_only_fields = ("id", "is_verified")

    def create(self, validated_data):
        user = self.context["request"].user
        password = validated_data.pop("password")
        validated_data["encrypted_password"] = encrypt(password)
        validated_data["user"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            validated_data["encrypted_password"] = encrypt(password)
        return super().update(instance, validated_data)


class EmailCredentialReadSerializer(serializers.ModelSerializer):
    """Serializer for reading email credentials (without password)"""
    class Meta:
        model = EmailCredential
        fields = ("id", "email", "smtp_host", "smtp_port", "is_verified")