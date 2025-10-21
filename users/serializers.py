from typing import Any

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'display_name',
            'organization', 'role', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    display_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'display_name']
        read_only_fields = ['id']

    def create(self, validated_data: dict[str, Any]) -> User:
        password = validated_data.pop('password')
        # Default username to email if not explicitly provided
        if not validated_data.get('username') and validated_data.get('email'):
            validated_data['username'] = validated_data['email']
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

