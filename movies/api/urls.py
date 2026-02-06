from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    home_api,
    movie_list_api,
    movie_detail_api,
    register_api,
    toggle_favorite_api,
    user_favorites_api,
    add_review_api,
)

urlpatterns = [
    # Home / Movies
    path('home/', home_api),
    path('movies/', movie_list_api),
    path('movies/<int:pk>/', movie_detail_api),

    # Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register_api),

    # Favorites
    path('favorites/', user_favorites_api),
    path('favorites/toggle/<int:movie_id>/', toggle_favorite_api),

    # Reviews
    path('movies/<int:movie_id>/review/', add_review_api),
]
