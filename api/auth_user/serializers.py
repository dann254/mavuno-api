from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.reverse import reverse_lazy
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from .models import User

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'password'
        )

    def create(self, validated_data):
        auth_user = User.objects.create_user(**validated_data)
        return auth_user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid email or password")

        try:
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)

            update_last_login(None, user)

            validation = {
                'access': access_token,
                'refresh': refresh_token,
                'email': user.email,
                'role': user.role,
            }

            return validation
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")


class UserListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    def get_url(self, obj):
        return reverse_lazy("users-detail", request=self.context['request'], kwargs={'uid':obj.uid})
    class Meta:
        model = User
        fields = (
            'uid',
            'email',
            'role',
            'url'
        )

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'uid',
            'email',
            'role'
        )

class RoleUpdateSerializer(serializers.ModelSerializer):
    role = serializers.IntegerField(max_value=3, min_value=2)
    class Meta:
        model = User
        fields = (
            'role',
        )

    def update(self, instance, validated_data):
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance
