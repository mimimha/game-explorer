from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
   path('posts/', views.PostListCreateView.as_view(), name='post-list'),
   path('posts/<int:post_id>/',
         views.PostDetailView.as_view(), name='post-detail'),
   path('posts/<int:post_id>/images/',
         views.PostImageListCreateView.as_view(), name='post-images'),
   path('posts/<int:post_id>/images/<int:image_id>/',
         views.PostImageDeleteView.as_view(), name='post-image-detail'),
   path('posts/<int:post_id>/comments/',
         views.CommentListCreateView.as_view(), name='comment-list'),
   path('comments/<int:comment_id>/',
         views.CommentDetailView.as_view(), name='comment-detail'),
]