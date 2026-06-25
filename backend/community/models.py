# community/models.py
from django.conf import settings
from django.db import models


class Post(models.Model):
    """ERD Post(post_id, user_id, game_id, title, content, category, ...)."""
    class Category(models.TextChoices):
        FREE = '자유', '자유'
        GUIDE = '공략', '공략'
        PARTY = '파티원모집', '파티원모집'

    post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='posts', db_column='user_id',
    )
    # 게임 연동(선택). 게임 태그 미선택 시 null.
    game = models.ForeignKey(
        'games.Game', on_delete=models.SET_NULL,
        related_name='posts', db_column='game_id',
        null=True, blank=True,
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.FREE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'post'
        ordering = ['-post_id']

    def __str__(self):
        return self.title


def _post_image_path(instance, filename):
    return f'posts/{instance.post_id}/{filename}'


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=_post_image_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_image'
        ordering = ['id']


class PostComment(models.Model):
    """ERD Post_Comment(comment_id, post_id, user_id, content, ...)."""
    comment_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments', db_column='post_id',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='comments', db_column='user_id',
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'post_comment'
        ordering = ['comment_id']

    def __str__(self):
        return f'{self.post.title} - comment {self.comment_id}'