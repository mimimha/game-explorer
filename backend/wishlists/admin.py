from django.contrib import admin
from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['wishlist_id', 'user', 'game', 'created_at']
    search_fields = ['user__nickname', 'game__title']