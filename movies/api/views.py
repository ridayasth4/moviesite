from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Q
from django.contrib.auth.models import User

from movies.models import Movie, Review, Favorite, Genre
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    ReviewSerializer
)


# ---------------- Home API ----------------
@api_view(['GET'])
@permission_classes([AllowAny])
def home_api(request):
    # Added select_related('genre') to save database hits
    base_queryset = Movie.objects.select_related('genre').annotate(
        avg_rating_val=Avg('reviews__rating')
    )

    featured = base_queryset.filter(featured=True).order_by('-created_at')[:6]
    latest = base_queryset.order_by('-release_date')[:4]
    trending = base_queryset.order_by('-avg_rating_val')[:4]

    return Response({
        "featured": MovieListSerializer(featured, many=True).data,
        "latest": MovieListSerializer(latest, many=True).data,
        "trending": MovieListSerializer(trending, many=True).data,
    })


# ---------------- Movie List API ----------------
@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list_api(request):
    # Added select_related and ordering
    movies = Movie.objects.select_related('genre').annotate(
        avg_rating_val=Avg('reviews__rating')
    ).order_by('-release_date')

    q = request.GET.get('q')
    if q:
        movies = movies.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(genre__name__icontains=q)
        )

    genre_id = request.GET.get('genre')
    if genre_id:
        movies = movies.filter(genre_id=genre_id)

    return Response(MovieListSerializer(movies, many=True).data)


# ---------------- Movie Detail API ----------------
@api_view(['GET'])
@permission_classes([AllowAny])
def movie_detail_api(request, pk):
    # Use get_object_or_404 to avoid 500 errors
    movie = get_object_or_404(
        Movie.objects.select_related('genre').annotate(
            avg_rating_val=Avg('reviews__rating')
        ),
        pk=pk
    )

    reviews = movie.reviews.all().select_related('user')

    return Response({
        "movie": MovieDetailSerializer(movie).data,
        "reviews": ReviewSerializer(reviews, many=True).data
    })


# ---------------- Auth & Actions ----------------

@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm = data.get('confirm_password')

    if password != confirm:
        return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
        return Response({"error": "Username or Email already taken"}, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create_user(username=username, email=email, password=password)
    return Response({"message": "Account created successfully"}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite_api(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        favorite.delete()
        return Response({"status": "removed", "is_favorite": False})
    return Response({"status": "added", "is_favorite": True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_favorites_api(request):
    fav_movies = Movie.objects.filter(favorited_by__user=request.user).select_related('genre')
    return Response(MovieListSerializer(fav_movies, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review_api(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    try:
        rating = int(request.data.get('rating', 0))
    except ValueError:
        return Response({"error": "Rating must be a number"}, status=status.HTTP_400_BAD_REQUEST)

    if not (1 <= rating <= 5):
        return Response({"error": "Rating must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)

    review, created = Review.objects.update_or_create(
        movie=movie,
        user=request.user,
        defaults={'rating': rating, 'comment': request.data.get('comment', '')}
    )
    return Response(ReviewSerializer(review).data)