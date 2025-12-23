from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username= serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = Profile
        fields = ['username', 'phone', 'bio', 'linkedin', 'github', 'skills', 'resume']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()