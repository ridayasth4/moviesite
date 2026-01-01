from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Movie
from django.shortcuts import get_object_or_404

# ---------------- Home ----------------
def home(request):
    return render(request, 'movies/home.html')

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
    return render(request, 'movies/movie_list.html', {'movies': movies})

# Movie Detail
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, 'movies/movie_detail.html', {'movie': movie})