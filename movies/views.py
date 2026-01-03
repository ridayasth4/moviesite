from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Movie, Favorite, Review
from django.core.paginator import Paginator
from django.db.models import Avg

# ---------------- Home ----------------
from django.db.models import Count

from django.db.models import Avg

def home(request):
    """Featured carousel + trending (top rated) + other movies grid."""

    # ---------------- Featured movies ----------------
    featured_movies = Movie.objects.filter(featured=True).order_by('-created_at')[:6]
    if not featured_movies.exists():
        featured_movies = Movie.objects.order_by('-created_at')[:6]

    # ---------------- Latest/Other movies ----------------
    other_movies = Movie.objects.exclude(
        id__in=[m.id for m in featured_movies]
    ).order_by('-created_at')

    # ---------------- Trending / Top Rated ----------------
    trending_movies = Movie.objects.annotate(avg_rating_val=Avg('reviews__rating'))\
                                   .order_by('-avg_rating_val')[:5]

    # ---------------- User favorites ----------------
    user_fav_ids = set(request.user.favorites.values_list('movie_id', flat=True)) if request.user.is_authenticated else set()

    # ---------------- Compute stars and avg_rating_value ----------------
    all_movies = list(featured_movies) + list(other_movies) + list(trending_movies)
    for movie in all_movies:
        # Use the annotated rating for trending if exists, else property
        avg = getattr(movie, 'avg_rating_val', None) or movie.avg_rating
        movie.avg_rating_value = avg
        movie.stars_list = [
            'full' if i <= avg else
            'half' if i - avg < 1 else
            'empty'
            for i in range(1, 6)
        ]

    # ---------------- Render ----------------
    return render(request, 'movies/home.html', {
        'movies': featured_movies,
        'other_movies': other_movies,
        'trending_movies': trending_movies,
        'user_fav_ids': user_fav_ids,
    })


# ---------------- Login ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, "Invalid username or password")
    return render(request, 'movies/login.html')


# ---------------- Logout ----------------
def logout_view(request):
    logout(request)
    return redirect('home')


# ---------------- Register ----------------
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken")
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')

    return render(request, 'movies/register.html')


# ---------------- Movie List ----------------
def movie_list(request):
    movies = Movie.objects.all().order_by('-release_date')

    if q := request.GET.get('q'):
        movies = movies.filter(title__icontains=q)
    if genre := request.GET.get('genre'):
        movies = movies.filter(genre__iexact=genre)

    paginator = Paginator(movies, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    genres = Movie.objects.values_list('genre', flat=True).distinct()
    user_fav_ids = set(request.user.favorites.values_list('movie_id', flat=True)) if request.user.is_authenticated else set()

    # Compute stars and avg_rating_value only for current page
    for movie in page_obj:
        avg = movie.avg_rating
        movie.avg_rating_value = avg
        movie.stars_list = [
            'full' if i <= avg else
            'half' if i - avg < 1 else
            'empty'
            for i in range(1, 6)
        ]

    return render(request, 'movies/movie_list.html', {
        'page_obj': page_obj,
        'genres': genres,
        'user_fav_ids': user_fav_ids,
        'request': request,
    })


# ---------------- Movie Detail ----------------
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    user_fav_ids = set(request.user.favorites.values_list('movie_id', flat=True)) if request.user.is_authenticated else set()
    reviews = movie.reviews.all()

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'user_fav_ids': user_fav_ids,
        'reviews': reviews,
        'avg_rating_value': movie.avg_rating,
        'stars_display': movie.stars_display,
        'review_stars_range': range(1, 6),
    })


# ---------------- Toggle Favorite ----------------
@login_required
def toggle_favorite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        favorite.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# ---------------- Add Review ----------------
@login_required
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        Review.objects.update_or_create(
            movie=movie,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
    return redirect('movie_detail', pk=movie.id)


# ---------------- Favorites List ----------------
@login_required
def favorites_list(request):
    fav_movies = Movie.objects.filter(favorited_by__user=request.user).order_by('-created_at')
    user_fav_ids = set(movie.id for movie in fav_movies)

    for movie in fav_movies:
        avg = movie.avg_rating
        movie.avg_rating_value = avg
        movie.stars_list = [
            'full' if i <= avg else
            'half' if i - avg < 1 else
            'empty'
            for i in range(1, 6)
        ]

    return render(request, 'movies/favorites.html', {
        'fav_movies': fav_movies,
        'user_fav_ids': user_fav_ids,
    })
