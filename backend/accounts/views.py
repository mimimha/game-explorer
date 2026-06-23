# accounts/views.py
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User, Follow, Medal
from .serializers import (
    UserSerializer, UserUpdateSerializer,
    PublicProfileSerializer, MedalSerializer,
)


class MeView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /accounts/me/  내 프로필 조회
    PATCH  /accounts/me/  내 프로필 수정
    DELETE /accounts/me/  회원 탈퇴
    """
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
        return Response(UserSerializer(request.user).data)


class UserProfileView(generics.RetrieveAPIView):
    """GET /accounts/users/{user_id}/  특정 유저 공개 프로필"""
    permission_classes = [AllowAny]
    serializer_class = PublicProfileSerializer
    lookup_url_kwarg = 'user_id'
    queryset = User.objects.all()


class FollowToggleView(APIView):
    """
    POST   /accounts/users/{user_id}/follow/  팔로우
    DELETE /accounts/users/{user_id}/follow/  언팔로우
    """
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


class MyMedalsView(generics.ListAPIView):
    """GET /accounts/me/medals/  내 획득 메달 목록"""
    permission_classes = [IsAuthenticated]
    serializer_class = MedalSerializer

    def get_queryset(self):
        return Medal.objects.filter(user=self.request.user)


class MyPageView(APIView):
    """
    GET /accounts/mypage/  마이페이지 집계 (찜/글/댓글/메달 수 + 묶음)
    ※ wishlist/posts/comments 는 해당 앱 모델 완성 후 채워진다(아래 TODO).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        def safe_count(related_name):
            mgr = getattr(user, related_name, None)
            return mgr.count() if mgr is not None else 0

        data = {
            'nickname': user.nickname,
            'profile_img': user.profile_img or None,
            'counts': {
                'wishlist': safe_count('wishlists'),     # TODO: wishlists 앱
                'posts': safe_count('posts'),            # TODO: community 앱
                'comments': safe_count('comments'),      # TODO: community 앱
                'medals': user.medals.count(),
            },
            'recent_wishlist': [],   # TODO: WishlistSerializer 연결
            'recent_posts': [],      # TODO: PostSerializer 연결
            'medals': MedalSerializer(user.medals.all(), many=True).data,
        }
        return Response(data)