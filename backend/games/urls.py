from django.urls import path
from . import views

app_name = 'games'  

urlpatterns = [
    path('games/', views.GameListView.as_view(), name='game-list'),
    path('games/recommended/',
         views.RecommendedGamesView.as_view(), name='game-recommended'),
    path('games/on-sale/',
         views.OnSaleGamesView.as_view(), name='game-on-sale'),
    path('games/new-releases/',
         views.NewReleaseGamesView.as_view(), name='game-new-releases'),
    path('games/filter-options/',
         views.FilterOptionsView.as_view(), name='game-filter-options'),
    path('games/suggest/',
         views.GameSuggestView.as_view(), name='game-suggest'),
    path('games/<int:game_id>/',
         views.GameDetailView.as_view(), name='game-detail'),
    path('games/<int:game_id>/videos/',
         views.GameVideosView.as_view(), name='game-videos'),
    path('games/<int:game_id>/posts/',
         views.GamePostsView.as_view(), name='game-posts'),
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
]