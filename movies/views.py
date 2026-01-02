from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Movie, Favorite, Review
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Avg


# ---------------- Home ----------------
def home(request):
    featured_movies = Movie.objects.filter(featured=True)

    if not featured_movies.exists():
        featured_movies = Movie.objects.all().order_by('-created_at')[:6]

    # Add user's favorites
    if request.user.is_authenticated:
        user_fav_ids = request.user.favorites.values_list('movie_id', flat=True)
    else:
        user_fav_ids = []

    context = {
        'movies': featured_movies,
        'user_fav_ids': user_fav_ids,
    }
    return render(request, 'movies/home.html', context)


# ---------------- Login ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
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
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')

    return render(request, 'movies/register.html')

# Movie List
def movie_list(request):
    movies = Movie.objects.all().order_by('-release_date')

    search_query = request.GET.get('q')
    genre_filter = request.GET.get('genre')

    if search_query:
        movies = movies.filter(title__icontains=search_query)

    if genre_filter:
        movies = movies.filter(genre__iexact=genre_filter)

    paginator = Paginator(movies, 6)  # 6 movies per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    genres = Movie.objects.values_list('genre', flat=True).distinct()

    # ✅ Add user's favorites (IDs only)
    if request.user.is_authenticated:
        user_fav_ids = request.user.favorites.values_list('movie_id', flat=True)
    else:
        user_fav_ids = []

    context = {
        'page_obj': page_obj,
        'genres': genres,
        'user_fav_ids': user_fav_ids,
    }

    return render(request, 'movies/movie_list.html', context)

# Movie Detail
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    #favourites
    if request.user.is_authenticated:
        user_fav_ids = request.user.favorites.values_list('movie_id', flat=True)
    else:
        user_fav_ids = []

    # Reviews
    reviews = movie.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    context = {
        'movie': movie,
        'user_fav_ids': user_fav_ids,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }

    return render(request, 'movies/movie_detail.html', context)


@login_required
def toggle_favorite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        # Already exists → remove it
        favorite.delete()

    return redirect(request.META.get('HTTP_REFERER', 'home'))

def add_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')

        review, created = Review.objects.update_or_create(
            movie=movie,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )

    return redirect('movie_detail', pk=movie.id)