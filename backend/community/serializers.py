from rest_framework import serializers
from .models import Post, PostComment
from games.models import Game


class AuthorSerializer(serializers.Serializer):
    """글·댓글에 박히는 작성자 요약."""
    id = serializers.IntegerField()
    nickname = serializers.CharField()
    profile_img = serializers.CharField(allow_blank=True, required=False)


class PostGameSerializer(serializers.Serializer):
    """글에 연동된 게임 요약 (없으면 null)."""
    id = serializers.IntegerField(source='game_id')
    title = serializers.CharField()
    capsule_url = serializers.CharField(allow_blank=True, required=False)


class PostListSerializer(serializers.ModelSerializer):
    """글 목록용."""
    id = serializers.IntegerField(source='post_id', read_only=True)
    author = serializers.SerializerMethodField()
    game = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(
        source='comments.count', read_only=True
    )

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'category', 'author', 'game',
            'comment_count', 'created_at',
        ]

    def get_author(self, obj):
        request = self.context.get('request')
        profile_img = obj.user.profile_img
        return {
            'id': obj.user.id,
            'nickname': obj.user.nickname,
            'profile_img': request.build_absolute_uri(profile_img.url)
                           if (request and profile_img) else None,
        }

    def get_game(self, obj):
        if not obj.game:
            return None
        return {
            'id': obj.game.game_id,
            'title': obj.game.title,
        }


class PostDetailSerializer(serializers.ModelSerializer):
    """글 상세용. is_author 포함."""
    id = serializers.IntegerField(source='post_id', read_only=True)
    author = serializers.SerializerMethodField()
    game = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(
        source='comments.count', read_only=True
    )
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'category', 'author', 'game',
            'comment_count', 'created_at', 'updated_at', 'is_author',
        ]

    def get_author(self, obj):
        request = self.context.get('request')
        profile_img = obj.user.profile_img
        return {
            'id': obj.user.id,
            'nickname': obj.user.nickname,
            'profile_img': request.build_absolute_uri(profile_img.url)
                           if (request and profile_img) else None,
        }

    def get_game(self, obj):
        if not obj.game:
            return None
        return {
            'id': obj.game.game_id,
            'title': obj.game.title,
            'capsule_url': obj.game.capsule_url or None,
        }

    def get_is_author(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user


class PostWriteSerializer(serializers.ModelSerializer):
    """글 작성·수정용. game_id 선택 (존재 검증 자동)."""
    game_id = serializers.PrimaryKeyRelatedField(
        source='game', queryset=Game.objects.all(),
        required=False, allow_null=True,
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'game_id']


class CommentSerializer(serializers.ModelSerializer):
    """댓글 목록·작성 응답용."""
    id = serializers.IntegerField(source='comment_id', read_only=True)
    author = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ['id', 'content', 'author', 'created_at', 'is_author']

    def get_author(self, obj):
        request = self.context.get('request')
        profile_img = obj.user.profile_img
        return {
            'id': obj.user.id,
            'nickname': obj.user.nickname,
            'profile_img': request.build_absolute_uri(profile_img.url)
                           if (request and profile_img) else None,
        }

    def get_is_author(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user


class CommentWriteSerializer(serializers.ModelSerializer):
    """댓글 작성·수정용."""
    class Meta:
        model = PostComment
        fields = ['content']