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
    path('accounts/users/<int:user_id>/<str:list_type>/',
         views.FollowListView.as_view(), name='follow-list'),
    # 알림
    path('accounts/notifications/', views.NotificationListView.as_view(), name='notif-list'),
    path('accounts/notifications/count/', views.NotificationCountView.as_view(), name='notif-count'),
    path('accounts/notifications/read-all/', views.NotificationReadAllView.as_view(), name='notif-read-all'),
    path('accounts/notifications/<int:notif_id>/read/', views.NotificationReadView.as_view(), name='notif-read'),
]