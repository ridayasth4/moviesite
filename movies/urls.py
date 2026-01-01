from django.urls import path
from . import views 


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),
]
