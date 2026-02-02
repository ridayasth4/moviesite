from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Movies
    path('movies/', views.movie_list, name='movie_list'),  # All movies
    path('movies/genre/<int:genre_id>/', views.movie_list, name='movie_list_by_genre'),  # By genre
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('movies/<int:pk>/watch/', views.watch_movie, name='watch_movie'),
    path('movies/<int:movie_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('movies/<int:movie_id>/review/', views.add_review, name='add_review'),
    path('movies/latest/', views.movie_list, {'filter_type': 'latest'}, name='latest_movies'),
    path('movies/top-rated/', views.movie_list, {'filter_type': 'top-rated'}, name='top_rated_movies'),
    path('movies/trending/', views.movie_list, {'filter_type': 'trending'}, name='trending_movies'),

    # Favorites
    path('movies/favorites/', views.favorites_list, name='favorites'),
]
