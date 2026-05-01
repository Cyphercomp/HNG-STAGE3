from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('id', 'created_at')




User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Include fields required by the Stage 3 spec
        fields = ['id', 'first_name', 'last_name', 'email', 'role'] 
        read_only_fields = ['id', 'email'] # Prevent users from changing their email manually if needed 