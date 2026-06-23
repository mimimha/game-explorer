from django.contrib import admin
from .models import Post, PostComment


class PostCommentInline(admin.TabularInline):
    model = PostComment
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['post_id', 'title', 'category', 'user', 'game', 'created_at']
    list_filter = ['category']
    search_fields = ['title', 'content']
    inlines = [PostCommentInline]


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['comment_id', 'post', 'user', 'created_at']
