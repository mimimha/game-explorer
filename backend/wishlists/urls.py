from django.urls import path
from . import views

app_name = 'wishlists'  

urlpatterns = [
   path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
   path('games/<int:game_id>/wishlist/',
         views.WishlistToggleView.as_view(), name='wishlist-toggle'),
]