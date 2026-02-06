from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db.models import Avg, Q
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from movies.models import Movie, Review
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    ReviewSerializer
)

# ---------------- Home API ----------------
@api_view(['GET'])
@permission_classes([AllowAny])
def home_api(request):
    featured = Movie.objects.filter(featured=True) \
        .annotate(avg_rating_val=Avg('reviews__rating'))[:6]

    latest = Movie.objects.order_by('-release_date') \
        .annotate(avg_rating_val=Avg('reviews__rating'))[:4]

    trending = Movie.objects.annotate(
        avg_rating_val=Avg('reviews__rating')
    ).order_by('-avg_rating_val')[:4]

    return Response({
        "featured": MovieListSerializer(featured, many=True).data,
        "latest": MovieListSerializer(latest, many=True).data,
        "trending": MovieListSerializer(trending, many=True).data,
    })


# ---------------- Movie List API ----------------
@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list_api(request):
    movies = Movie.objects.annotate(avg_rating_val=Avg('reviews__rating'))

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
    movie = Movie.objects.annotate(
        avg_rating_val=Avg('reviews__rating')
    ).get(pk=pk)

    reviews = movie.reviews.all()

    return Response({
        "movie": MovieDetailSerializer(movie).data,
        "reviews": ReviewSerializer(reviews, many=True).data
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    if password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({"message": "Account created successfully"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite_api(request, movie_id):
    from movies.models import Movie, Favorite

    movie = get_object_or_404(Movie, id=movie_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        favorite.delete()
        return Response({"status": "removed"})
    return Response({"status": "added"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_favorites_api(request):
    fav_movies = Movie.objects.filter(favorited_by__user=request.user)
    from .serializers import MovieListSerializer
    return Response(MovieListSerializer(fav_movies, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review_api(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    rating = int(request.data.get('rating', 0))
    comment = request.data.get('comment', '')

    if rating < 1 or rating > 5:
        return Response({"error": "Rating must be 1-5"}, status=status.HTTP_400_BAD_REQUEST)

    review, created = Review.objects.update_or_create(
        movie=movie,
        user=request.user,
        defaults={'rating': rating, 'comment': comment}
    )
    from .serializers import ReviewSerializer
    return Response(ReviewSerializer(review).data)
