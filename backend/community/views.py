from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Post, PostComment, PostImage
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostWriteSerializer,
    CommentSerializer, CommentWriteSerializer, PostImageSerializer,
)


class PostListCreateView(generics.ListCreateAPIView):
    """
    GET  /posts/  글 목록 (category 필터·검색·페이지네이션)
    POST /posts/  글 작성 (토큰 필요)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Post.objects.select_related('user', 'game')\
                         .prefetch_related('comments')
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        q = self.request.query_params.get('q')
        if q:
            search_type = self.request.query_params.get('search_type', 'title')
            if search_type == 'author':
                qs = qs.filter(user__nickname__icontains=q)
            else:
                qs = qs.filter(title__icontains=q)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostWriteSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # 작성 후 상세 형태로 응답
        write = self.get_serializer(data=request.data)
        write.is_valid(raise_exception=True)
        post = write.save(user=request.user)
        if request.user.posts.count() == 1:
            from accounts.medal_service import award_medal
            award_medal(request.user, '첫 교신')
        detail = PostDetailSerializer(post, context={'request': request})
        return Response(detail.data, status=status.HTTP_201_CREATED)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /posts/{post_id}/  상세
    PATCH  /posts/{post_id}/  수정 (작성자만)
    DELETE /posts/{post_id}/  삭제 (작성자만)
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    queryset = Post.objects.select_related('user', 'game')\
                           .prefetch_related('comments')
    lookup_url_kwarg = 'post_id'
    http_method_names = ['get', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return PostWriteSerializer
        return PostDetailSerializer

    def update(self, request, *args, **kwargs):
        # 수정 후 상세 형태로 응답
        super().update(request, *args, **kwargs)
        post = self.get_object()
        return Response(
            PostDetailSerializer(post, context={'request': request}).data
        )


class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /posts/{post_id}/comments/  댓글 목록
    POST /posts/{post_id}/comments/  댓글 작성 (토큰 필요)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # 댓글은 전체 반환

    def get_queryset(self):
        return PostComment.objects.filter(post_id=self.kwargs['post_id'])\
                                  .select_related('user')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentWriteSerializer
        return CommentSerializer

    def create(self, request, *args, **kwargs):
        write = self.get_serializer(data=request.data)
        write.is_valid(raise_exception=True)
        comment = write.save(
            user=request.user, post_id=self.kwargs['post_id']
        )
        if request.user.comments.count() >= 20:
            from accounts.medal_service import award_medal
            award_medal(request.user, '댓글 요정')
        from rest_framework.response import Response
        from rest_framework import status
        out = CommentSerializer(comment, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    PATCH  /comments/{comment_id}/  수정 (작성자만)
    DELETE /comments/{comment_id}/  삭제 (작성자만)
    """
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    queryset = PostComment.objects.select_related('user')
    lookup_url_kwarg = 'comment_id'
    http_method_names = ['patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return CommentWriteSerializer
        return CommentSerializer

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        comment = self.get_object()
        return Response(
            CommentSerializer(comment, context={'request': request}).data
        )


class PostImageListCreateView(generics.GenericAPIView):
    """
    POST /posts/{post_id}/images/  이미지 업로드 (작성자만)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id, user=request.user)
        files = request.FILES.getlist('images')
        if not files:
            return Response({'detail': '이미지를 선택해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        created = []
        for f in files:
            img = PostImage.objects.create(post=post, image=f)
            created.append(PostImageSerializer(img, context={'request': request}).data)
        return Response(created, status=status.HTTP_201_CREATED)


class PostImageDeleteView(generics.DestroyAPIView):
    """
    DELETE /posts/{post_id}/images/{image_id}/  이미지 삭제 (작성자만)
    """
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'image_id'

    def get_object(self):
        return get_object_or_404(PostImage, pk=self.kwargs['image_id'], post__user=self.request.user)