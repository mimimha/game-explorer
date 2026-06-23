# accounts/serializers.py
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

from .models import User, UserMedal


class MedalSerializer(serializers.ModelSerializer):
    """
    me/medals · 프로필의 메달 표시용.
    UserMedal(획득 기록) 기준으로 카탈로그 정보(medal_name 등)를 평탄화.
    """
    id = serializers.IntegerField(source='medal.medal_id', read_only=True)
    medal_name = serializers.CharField(source='medal.medal_name', read_only=True)
    description = serializers.CharField(
        source='medal.description', read_only=True
    )
    icon_url = serializers.CharField(source='medal.icon_url', read_only=True)

    class Meta:
        model = UserMedal
        fields = ['id', 'medal_name', 'description', 'icon_url', 'earned_at']


class UserSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = User
        fields = ['nickname', 'birth_date', 'profile_img']


class PublicProfileSerializer(serializers.ModelSerializer):
    follower_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.SerializerMethodField()
    medals = MedalSerializer(source='user_medals', many=True, read_only=True)

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