from django.urls import path
from . import views


app_name = 'recommendations'  

urlpatterns = [
    path('recommend/', views.RecommendView.as_view(), name='recommend'),
    path('recommend/logs/',
         views.RecommendLogListView.as_view(), name='recommend-logs'),
    path('recommend/logs/<int:log_id>/',
         views.RecommendLogDetailView.as_view(), name='recommend-log-detail'),
    path('recommend/logs/<int:log_id>/delete/',
         views.RecommendLogDestroyView.as_view(), name='recommend-log-delete'),
]