# accounts/views.py
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User, Follow, UserMedal, Notification
from .serializers import (
    UserSerializer, UserUpdateSerializer,
    PublicProfileSerializer, MedalSerializer, NotificationSerializer,
)


class MeView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /accounts/me/"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer

    def patch(self, request, *args, **kwargs):
        super().patch(request, *args, **kwargs)
        from .medal_service import award_medal
        award_medal(request.user, '탐험대의 일원')
        return Response(UserSerializer(request.user, context={'request': request}).data)


class UserProfileView(APIView):
    """GET /accounts/users/{user_id}/  공개 프로필 + 활동 집계"""
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)

        from community.models import Post
        from community.serializers import PostListSerializer
        from wishlists.models import Wishlist
        from wishlists.serializers import WishlistItemSerializer
        from recommendations.models import RecommendationLog
        from recommendations.serializers import RecommendationLogListSerializer

        recent_posts = Post.objects.filter(user=target) \
                                   .select_related('user', 'game') \
                                   .prefetch_related('comments')[:5]
        recent_wishlist = Wishlist.objects.filter(user=target) \
                                          .select_related('game') \
                                          .prefetch_related('game__genres')
        recent_logs = RecommendationLog.objects.filter(user=target) \
                                               .prefetch_related('results')[:3]

        is_following = False
        if request.user.is_authenticated:
            is_following = target.follower_relations.filter(follower=request.user).exists()

        data = {
            'id': target.id,
            'nickname': target.nickname,
            'profile_img': request.build_absolute_uri(target.profile_img.url)
                           if target.profile_img else None,
            'birth_date': target.birth_date.isoformat() if target.birth_date else None,
            'follower_count': target.follower_count,
            'following_count': target.following_count,
            'is_following': is_following,
            'medals': MedalSerializer(
                target.user_medals.select_related('medal'), many=True
            ).data,
            'counts': {
                'wishlist': target.wishlists.count(),
                'posts': target.posts.count(),
                'comments': target.comments.count(),
                'medals': target.user_medals.count(),
            },
            'recent_posts': PostListSerializer(
                recent_posts, many=True, context={'request': request}
            ).data,
            'recent_wishlist': WishlistItemSerializer(
                recent_wishlist, many=True, context={'request': request}
            ).data,
            'recent_logs': RecommendationLogListSerializer(
                recent_logs, many=True
            ).data,
        }
        return Response(data)


class FollowToggleView(APIView):
    """POST·DELETE /accounts/users/{user_id}/follow/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        if target == request.user:
            return Response(
                {'detail': '자기 자신은 팔로우할 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Follow.objects.get_or_create(follower=request.user, following=target)
        return Response({
            'is_following': True,
            'follower_count': target.follower_count,
        })

    def delete(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        Follow.objects.filter(follower=request.user, following=target).delete()
        return Response({
            'is_following': False,
            'follower_count': target.follower_count,
        })


class FollowListView(APIView):
    """GET /accounts/users/{user_id}/followers/  또는  /following/"""
    permission_classes = [AllowAny]

    def get(self, request, user_id, list_type):
        target = get_object_or_404(User, pk=user_id)
        if list_type == 'followers':
            users = User.objects.filter(following_relations__following=target)
        else:
            users = User.objects.filter(follower_relations__follower=target)

        data = [
            {
                'id': u.id,
                'nickname': u.nickname,
                'profile_img': request.build_absolute_uri(u.profile_img.url)
                               if u.profile_img else None,
            }
            for u in users
        ]
        return Response(data)


class MyMedalsView(generics.ListAPIView):
    """GET /accounts/me/medals/  내 획득 메달"""
    permission_classes = [IsAuthenticated]
    serializer_class = MedalSerializer

    def get_queryset(self):
        return UserMedal.objects.filter(user=self.request.user)\
                                .select_related('medal')


class NotificationListView(generics.ListAPIView):
    """GET /accounts/notifications/  내 알림 목록 (최신순, 최대 100개)"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('actor')[:100]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class NotificationCountView(APIView):
    """GET /accounts/notifications/count/  읽지 않은 알림 수"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({'count': count})


class NotificationReadView(APIView):
    """PATCH /accounts/notifications/{notif_id}/read/  단건 읽음 처리"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, notif_id):
        notif = get_object_or_404(Notification, pk=notif_id, recipient=request.user)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return Response({'ok': True})


class NotificationReadAllView(APIView):
    """POST /accounts/notifications/read-all/  전체 읽음 처리"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        return Response({'ok': True})


class MyPageView(APIView):
    """GET /accounts/mypage/  마이페이지 집계"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        from community.models import Post
        from community.serializers import PostListSerializer
        recent_posts = Post.objects.filter(user=user)\
                                   .select_related('user', 'game')\
                                   .prefetch_related('comments')[:5]

        from wishlists.models import Wishlist
        from wishlists.serializers import WishlistItemSerializer
        recent_wishlist = Wishlist.objects.filter(user=user)\
                                          .select_related('game')\
                                          .prefetch_related('game__genres')

        data = {
            'nickname': user.nickname,
            'profile_img': request.build_absolute_uri(user.profile_img.url) if user.profile_img else None,
            'counts': {
                'wishlist': user.wishlists.count(),
                'posts': user.posts.count(),
                'comments': user.comments.count(),
                'medals': user.user_medals.count(),
            },
            'recent_wishlist': WishlistItemSerializer(
                recent_wishlist, many=True, context={'request': request}
            ).data,
            'recent_posts': PostListSerializer(
                recent_posts, many=True, context={'request': request}
            ).data,
            'medals': MedalSerializer(
                user.user_medals.select_related('medal'), many=True
            ).data,
        }
        return Response(data)