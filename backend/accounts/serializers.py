# accounts/serializers.py
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

from .models import User, Medal


class MedalSerializer(serializers.ModelSerializer):
    """me/medals · 프로필의 메달 표시용."""
    id = serializers.IntegerField(source='medal_id', read_only=True)

    class Meta:
        model = Medal
        fields = ['id', 'medal_name']


class UserSerializer(serializers.ModelSerializer):
    """내 프로필 조회(GET /accounts/me/) 응답."""
    follower_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'nickname', 'birth_date',
            'profile_img', 'follower_count', 'following_count', 'date_joined',
        ]
        read_only_fields = ['id', 'username', 'email', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    """내 프로필 수정(PATCH /accounts/me/)."""
    class Meta:
        model = User
        fields = ['nickname', 'birth_date', 'profile_img']


class PublicProfileSerializer(serializers.ModelSerializer):
    """특정 유저 공개 프로필(GET /accounts/users/{id}/)."""
    follower_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.SerializerMethodField()
    medals = MedalSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'nickname', 'profile_img',
            'follower_count', 'following_count', 'is_following', 'medals',
        ]

    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.follower_relations.filter(follower=request.user).exists()


class CustomRegisterSerializer(RegisterSerializer):
    """dj-rest-auth 회원가입에 nickname/birth_date 추가."""
    nickname = serializers.CharField(max_length=50)
    birth_date = serializers.DateField(required=False, allow_null=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['nickname'] = self.validated_data.get('nickname', '')
        data['birth_date'] = self.validated_data.get('birth_date', None)
        return data

    def save(self, request):
        user = super().save(request)
        user.nickname = self.cleaned_data.get('nickname')
        user.birth_date = self.cleaned_data.get('birth_date')
        user.save()
        return user