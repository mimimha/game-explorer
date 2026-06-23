from django.urls import path
from . import views

app_name = 'accounts'  

urlpatterns = [
    path('accounts/me/', views.MeView.as_view(), name='me'),
    path('accounts/me/medals/', views.MyMedalsView.as_view(), name='my-medals'),
    path('accounts/mypage/', views.MyPageView.as_view(), name='mypage'),
    path('accounts/users/<int:user_id>/',
         views.UserProfileView.as_view(), name='user-profile'),
    path('accounts/users/<int:user_id>/follow/',
         views.FollowToggleView.as_view(), name='follow-toggle'),
]