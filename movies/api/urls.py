from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    home_api, movie_list_api, movie_detail_api,
    register_api, toggle_favorite_api,
    user_favorites_api, add_review_api
)

urlpatterns = [
    # Home / Movies
    path('home/', home_api, name='api_home'),
    path('movies/', movie_list_api, name='api_movie_list'),
    path('movies/<int:pk>/', movie_detail_api, name='api_movie_detail'),

    # Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register_api, name='api_register'),

    # Favorites
    path('favorites/', user_favorites_api, name='api_user_favorites'),
    path('favorites/toggle/<int:movie_id>/', toggle_favorite_api, name='api_toggle_favorite'),

    # Reviews
    path('movies/<int:movie_id>/review/', add_review_api, name='api_add_review'),
]