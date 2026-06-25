# accounts/serializers.py
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

from .models import User, UserMedal, Notification


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


class NotificationSerializer(serializers.ModelSerializer):
    actor_id = serializers.IntegerField(source='actor.id', read_only=True, default=None)
    actor_nickname = serializers.CharField(source='actor.nickname', read_only=True, default=None)
    actor_profile_img = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'notif_type', 'actor_id', 'actor_nickname', 'actor_profile_img',
            'target_id', 'target_title', 'message', 'is_read', 'created_at',
        ]

    def get_actor_profile_img(self, obj):
        if not obj.actor or not obj.actor.profile_img:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.actor.profile_img.url)
        return obj.actor.profile_img.url


class CustomRegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField(max_length=50)
    birth_date = serializers.DateField(required=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['nickname'] = self.validated_data.get('nickname', '')
        data['birth_date'] = self.validated_data.get('birth_date')
        return data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        if 'password1' in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data['password1'], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(str(exc))
        # nickname, birth_date를 user.save() 전에 세팅 (NOT NULL 제약 준수)
        user.nickname = self.cleaned_data.get('nickname', '')
        user.birth_date = self.cleaned_data.get('birth_date')
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        from .medal_service import award_medal
        award_medal(user, '발자국 시작')
        return user